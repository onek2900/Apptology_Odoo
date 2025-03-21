# -*- coding: utf-8 -*-
import json
import logging
import re
from odoo import fields, http
from odoo.http import request, Response
from datetime import datetime
import pytz

_logger = logging.getLogger(__name__)


class DeliverectWebhooks(http.Controller):
    """Controller for handling Deliverect webhooks"""

    def _convert_utc_to_user_tz(self,timezone, utc_time_str):
        """Convert an ISO 8601 UTC time string to the specified timezone.

        :param str timezone: The target timezone (e.g., 'Europe/Brussels').
        :param str utc_time_str: The UTC time in ISO 8601 format.
        :return: The converted datetime in the specified timezone or False if input is invalid.
        """
        if not utc_time_str:
            return False
        try:
            utc_time = datetime.fromisoformat(utc_time_str.replace("Z", "+00:00"))
            local_tz = pytz.timezone(timezone or "UTC")
            local_time = utc_time.astimezone(local_tz)
            return fields.Datetime.to_string(local_time)
        except ValueError as e:
            _logger.error(f"Time conversion error: {e}")
            return False

    def find_partner(self,channel_id):
        """Find or create a partner based on the given channel ID.

        :param int channel_id: The channel ID to search for the partner.
        :return: The ID of the found or newly created partner.
        """
        partner = request.env['res.partner'].sudo().search([('active','=',True),
                                                            ('channel_id', '=', channel_id)],
                                                           limit=1)
        if not partner:
            request.env['deliverect.channel'].sudo().update_channel()
            partner = request.env['res.partner'].sudo().search([('channel_id', '=', channel_id)], limit=1) or \
                      request.env['res.partner'].sudo().create({'name': "DELIVERECT", 'channel_id': channel_id})

        return partner.id

    def generate_order_notification(self,pos_id, order_status):
        """Generate a notification for new online orders.

        :param int pos_id: The POS order ID.
        :param str order_status: The status of the order "success" or "failure".
        """
        channel = f"new_pos_order_{pos_id}"
        request.env["bus.bus"]._sendone(channel, "notification", {
            "channel": channel,
            "order_status": order_status
        })

    def generate_data(self, pos_id):
        """Generate data for the POS order.

        :param int pos_id: The POS configuration ID.
        """
        pos_config = request.env['pos.config'].sudo().browse(pos_id)
        product_data = pos_config.create_deliverect_product_data()
        account_id = pos_config.account_id
        location_id = pos_config.location_id
        return {
            "priceLevels": [],
            'categories': [],
            'products': product_data,
            "accountId": account_id,
            "locationId": location_id
        }

    def generate_pos_reference(self,channel_order_id):
        """Generate a unique POS reference from the channel order ID for online orders.

        :param str channel_order_id: The order ID from the channel.
        """
        numeric_part = ''.join(filter(str.isdigit, channel_order_id))
        digits = numeric_part.zfill(12)
        pos_reference = f"Online-Order {digits[:5]}-{digits[5:8]}-{digits[8:]}"
        return pos_reference


    def create_order_line(self, product_id, qty, note):
        """Create an order line for a given product.

        :param int product_id: The ID of the product.
        :param float qty: The quantity of the product.
        :param str note: Additional note for the product passed by the customer.
        """
        product = request.env['product.product'].sudo().search(
            [('id', '=', product_id)],
            limit=1)
        if product:
            product_data = product.taxes_id.compute_all(
                product.lst_price,
                currency=product.currency_id,
                quantity=qty,
                product=product,
                partner=request.env['res.partner'].sudo()
            )
            line_vals = {
                'full_product_name': product.name,
                'product_id': product.id,
                'price_unit': product.lst_price,
                'qty': qty,
                'price_subtotal': product_data.get('total_excluded'),
                'price_subtotal_incl': product_data.get('total_included'),
                'discount': 0,
                'note': note,
                'tax_ids': [(6, 0, product.taxes_id.ids)]
            }
            return line_vals
        else:
            raise Exception("Product Not found")

    def create_order_data(self, data, pos_id):
        """
        Generate POS order data from Deliverect order details.

        :param dict data: data received from the webhook containing order details.
        :param int pos_id: The POS configuration ID.
        """
        pos_reference = self.generate_pos_reference(data['channelOrderId'])
        pos_config = request.env['pos.config'].sudo().browse(pos_id)
        is_auto_approve = pos_config.auto_approve
        if not pos_config.current_session_id:
            _logger.error(f"No active session for POS config {pos_config.id}")
            raise Exception('Session not active')
        try:
            current_session = pos_config.current_session_id
            sequence_code = f"pos.order_{current_session.id}"
            ir_sequence = request.env['ir.sequence'].sudo().search([
                ('code', '=', sequence_code),
                ('company_id', '=', pos_config.company_id.id)
            ], limit=1)
            if not ir_sequence:
                # check for existing online order sequence
                sequence_code = f"online_pos.order_{current_session.id}"
                ir_sequence = request.env['ir.sequence'].sudo().search([
                    ('code', '=', sequence_code),
                    ('company_id', '=', pos_config.company_id.id)
                ], limit=1)
            if not ir_sequence:
                # create new online order sequence
                ir_sequence = request.env['ir.sequence'].sudo().create({
                    'code': sequence_code,
                    'company_id': pos_config.company_id.id,
                    'padding': 4,
                    'prefix': 'Online',
                    'name': 'Online Sequence',
                    'number_increment': 1,
                })
                _logger.error(f"Standard POS sequence not found - created New one: {ir_sequence.code}")
            sequence_str = ir_sequence.sudo().next_by_id()
            sequence_number = re.findall(r'\d+', sequence_str)[0]
            order_lines = []
            total_untaxed = 0
            total_taxed = 0
            for item in data.get('items'):
                if item.get("plu").split('-')[0] == 'VAR_PRD':
                    if item.get('subItems'):
                        for sub_item in item.get('subItems'):
                            sub_item_line_vals = self.create_order_line(int(sub_item.get('plu').split('-')[1]),
                                                                        item.get('quantity'),
                                                                        item.get('remark', ""))
                            total_taxed += sub_item_line_vals.get('price_subtotal_incl')
                            total_untaxed += sub_item_line_vals.get('price_subtotal')
                            order_lines.append((0, 0, sub_item_line_vals))
                else:
                    line_vals = self.create_order_line(int(item.get('plu').split('-')[1]), item.get('quantity'),
                                                       item.get('remark', ""))
                    total_taxed += line_vals.get('price_subtotal_incl')
                    total_untaxed += line_vals.get('price_subtotal')
                    order_lines.append((0, 0, line_vals))
                    if item.get('subItems'):
                        for sub_item in item.get('subItems'):
                            sub_item_line_vals = self.create_order_line(int(sub_item.get('plu').split('-')[1]),
                                                                        item.get('quantity'),
                                                                        sub_item.get('remark', ""))
                            total_taxed += sub_item_line_vals.get('price_subtotal_incl')
                            total_untaxed += sub_item_line_vals.get('price_subtotal')
                            order_lines.append((0, 0, sub_item_line_vals))
            order_data = {
                'config_id': pos_config.id,
                'company_id': pos_config.company_id.id,
                'note': data.get('note', ''),
                'amount_paid': total_taxed,
                'amount_return': 0.0,
                'amount_tax': total_taxed - total_untaxed,
                'amount_total': total_taxed,
                'fiscal_position_id': False,
                'pricelist_id': pos_config.pricelist_id.id,
                'lines': order_lines,
                'name': pos_reference,
                'pos_reference': pos_reference,
                'order_payment_type': str(data.get('payment').get('type')),
                'partner_id': self.find_partner(data.get('channel')),
                'date_order': fields.Datetime.to_string(fields.Datetime.now()),
                'session_id': pos_config.current_session_id.id,
                'sequence_number': sequence_number,
                'user_id': pos_config.current_user_id.id,
                'is_online_order': True,
                'online_order_id': data.get('_id'),
                'online_order_status': 'approved' if is_auto_approve else 'open',
                'order_type': str(data.get('orderType')),
                'online_order_paid': data.get('orderIsAlreadyPaid'),
                'channel_discount': data.get('discountTotal') / 100,
                'channel_service_charge': data.get('serviceCharge') / 100,
                'channel_delivery_charge': data.get('deliveryCost') / 100,
                'channel_tip_amount': data.get('tip') / 100,
                'channel_total_amount': data.get('payment').get('amount') / 100,
                'bag_fee': data.get('bagFee') / 100,
                'delivery_note': data.get('deliveryAddress', {}).get('extraAddressInfo', ''),
                'channel_order_reference': data.get('channelOrderDisplayId'),
                'pickup_time':self._convert_utc_to_user_tz(pos_config.current_user_id.tz,data.get('pickupTime')),
                'delivery_time': self._convert_utc_to_user_tz(pos_config.current_user_id.tz,data.get('deliveryTime')),
                'channel_name': request.env['deliverect.channel'].sudo().search([('channel_id', '=',
                                                                                  data.get("channel"))],
                                                                                limit=1).name,
                'customer_name': data.get('customer', {}).get('name'),
                'customer_company_name': data.get('customer', {}).get('companyName'),
                'customer_email': data.get('customer', {}).get('email'),
                'customer_note': data.get('customer', {}).get('note'),
                'channel_tax':data.get('taxTotal')/100,
            }
            return order_data
        except Exception as e:
            _logger.error(f"Failed to create order data: {str(e)}")
            raise Exception(f"Failed to create order data :{str(e)}")

    @http.route('/deliverect/pos/products/<int:pos_id>', type='http', methods=['GET'], auth="none",
                csrf=False)
    def sync_products(self, pos_id):
        """
        Webhook for syncing products with Deliverect.

        :param int pos_id: The POS ID passed by Deliverect.
        """
        pos_configuration = request.env['pos.config'].sudo().browse(pos_id)
        try:
            product_data = self.generate_data(pos_configuration.id)
            return request.make_response(
                json.dumps(product_data),
                headers={'Content-Type': 'application/json'},
                status=200
            )
        except Exception as e:
            _logger.error(f"product sync error: {str(e)}")
            return request.make_response('', status=500)

    @http.route('/deliverect/pos/orders/<int:pos_id>', type='http', methods=['POST'], auth='none',
                csrf=False)
    def receive_pos_order(self, pos_id):
        """
        Webhook for receiving pos orders from Deliverect.

        :param int pos_id: The POS ID passed by Deliverect.
        """
        pos_configuration = request.env['pos.config'].sudo().browse(pos_id)
        try:
            deliverect_payment_method = request.env.ref("apptology_deliverect.pos_payment_method_deliverect")
            data = json.loads(request.httprequest.data)
            if data['status'] == 100 and data['_id']:
                order = request.env['pos.order'].sudo().search([('online_order_id', '=', data['_id'])], limit=1)
                order.write({
                    'order_status': 'cancel',
                    'online_order_status': 'cancelled',
                    'declined_time': fields.Datetime.now()
                })
                refund_action = order.refund()
                refund = request.env['pos.order'].sudo().browse(refund_action['res_id'])
                payment_context = {"active_ids": refund.ids, "active_id": refund.id}
                refund_payment = request.env['pos.make.payment'].sudo().with_context(**payment_context).create({
                    'amount': refund.amount_total,
                    'payment_method_id': deliverect_payment_method.id,
                })
                refund_payment.with_context(**payment_context).check()
            else:
                pos_order_data = self.create_order_data(data, pos_configuration.id)
                if pos_order_data:
                    order = request.env['pos.order'].sudo().create(pos_order_data)
                    if data['orderIsAlreadyPaid']:
                        payment_context = {"active_ids": order.ids, "active_id": order.id}
                        order_payment = request.env['pos.make.payment'].with_user(
                            pos_configuration.current_user_id.id).sudo(
                        ).with_context(
                            **payment_context).create({
                            'amount': order.amount_total,
                            'payment_method_id': deliverect_payment_method.id,
                        })
                        order_payment.with_context(**payment_context).check()
                    self.generate_order_notification(pos_configuration.id, 'success')
                    return Response(
                        json.dumps({'status': 'success', 'message': 'Order created',
                                    'order_id': order.id}),
                        content_type='application/json',
                        status=200
                    )
        except Exception as e:
            _logger.error(f"Error processing order webhook: {str(e)}")
            self.generate_order_notification(pos_configuration.id, 'failure')
            return Response(
                json.dumps({
                    'status': 'Error',
                    'message': f'Message: {e}',
                }),
                content_type='application/json',
                status=400
            )

    @http.route('/deliverect/pos/register', type='http', methods=['POST'], auth="none", csrf=False)
    def register_pos(self):
        """
        Webhook for registering POS with Deliverect.
        """
        config_param = request.env['ir.config_parameter'].sudo()
        base_url = config_param.get_param('web.base.url')
        try:
            data = json.loads(request.httprequest.data)
            pos_id = int(data.get('externalLocationId'))
            pos_configuration = request.env['pos.config'].sudo().browse(pos_id)
            pos_configuration.write({
                'account_id': data.get('accountId'),
                'location_id': data.get('locationId'),
            })
            is_channel_present = pos_configuration.create_customers_channel()
            request.env['deliverect.allergens'].sudo().update_allergens()
            if is_channel_present['params']['title'] == 'Failure':
                pos_configuration.write({
                    'status_message': f"{is_channel_present['params']['message']}",
                })
                return request.make_response(
                    json.dumps({'error': is_channel_present['params']['message']}),
                    headers=[('Content-Type', 'application/json')]
                )
            else:
                pos_configuration.write({
                    'status_message': f"POS Registration Successful"
                })
                response_data = {
                    "ordersWebhookURL": f"{base_url}/deliverect/pos/orders/{pos_id}",
                    "syncProductsURL": f"{base_url}/deliverect/pos/products/{pos_id}",
                    "syncTablesURL": "",
                    "syncFloorsURL": "",
                    "operationsWebhookURL": "",
                    "storeStatusWebhookURL": ""
                }
                return request.make_response(
                    json.dumps(response_data),
                    headers=[('Content-Type', 'application/json')]
                )

        except Exception as e:
            _logger.error(f"Registration error: {str(e)}")
            return request.make_response(
                json.dumps({'error': str(e)}),
                headers=[('Content-Type', 'application/json')]
            )

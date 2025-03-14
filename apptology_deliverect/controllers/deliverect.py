# -*- coding: utf-8 -*-
import json
import logging
import re
from odoo import fields, http, _
from odoo.http import request, Response

_logger = logging.getLogger(__name__)


class DeliverectWebhooks(http.Controller):
    """Controller for handling Deliverect webhooks and API integration."""

    @staticmethod
    def find_partner(channel_id):
        """function for finding partner from channel id"""
        partner = request.env['res.partner'].sudo().search([('channel_id', '=', channel_id)])
        if not partner:
            partner = request.env['res.partner'].sudo().create({
                'name': f"DELIVERECT",
                'channel_id': channel_id,
            })
        return partner.id


    @staticmethod
    def generate_order_notification(pos_id):
        """function for generating notification for pos order"""
        _logger.info(f"generating notification in pos id :{pos_id}")
        channel = f"new_pos_order_{pos_id}"
        request.env["bus.bus"]._sendone(channel, "notification", {
            "channel": channel,
        })

    @staticmethod
    def generate_data(self, pos_id):
        """function for generating data for pos order"""
        pos_config = request.env['pos.config'].sudo().browse(pos_id)
        product_data = pos_config.create_deliverect_product_data()
        print(product_data)
        account_id = pos_config.account_id
        location_id = pos_config.location_id
        return {
            "priceLevels": [],
            'categories': [],
            'products': product_data,
            "accountId": account_id,
            "locationId": location_id
        }

    @staticmethod
    def generate_pos_reference(channel_order_id):
        """Function for generating a unique POS reference"""
        numeric_part = ''.join(filter(str.isdigit, channel_order_id))
        digits = numeric_part.zfill(12)
        pos_reference = f"Online-Order {digits[:5]}-{digits[5:8]}-{digits[8:]}"
        return pos_reference

    @staticmethod
    def create_order_data(self, data, pos_id):
        print(json.dumps(data, indent=4))
        """function for pos order data from deliverect data"""
        pos_reference = self.generate_pos_reference(data['channelOrderId'])
        pos_config = request.env['pos.config'].sudo().browse(pos_id)
        is_auto_approve = pos_config.auto_approve
        if not pos_config.current_session_id:
            _logger.error(f"No active session for POS config {pos_config.id}")
            return False
        try:
            current_session = pos_config.current_session_id
            sequence_code = f"pos.order_{current_session.id}"
            ir_sequence = request.env['ir.sequence'].sudo().search([
                ('code', '=', sequence_code),
                ('company_id', '=', pos_config.company_id.id)
            ], limit=1)
            if not ir_sequence:
                sequence_code = f"online_pos.order_{current_session.id}"
                ir_sequence = request.env['ir.sequence'].sudo().search([
                    ('code', '=', sequence_code),
                    ('company_id', '=', pos_config.company_id.id)
                ], limit=1)
            if not ir_sequence:
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
            print(ir_sequence)
            order_data = {}
            order_lines = []
            print(data['items'])
            for item in data['items']:
                product = request.env['product.product'].sudo().search(
                    [('id', '=', int(item['plu'].split('-')[1]))],
                    limit=1)
                if product:
                    order_lines.append((0, 0, {
                        'full_product_name': product.name,
                        'product_id': product.product_variant_id.id,
                        'price_unit': item['price'] / 100,
                        'qty': item['quantity'],
                        'price_subtotal': item['price'] * item['quantity'] / 100,
                        'price_subtotal_incl': item['price'] * item['quantity'] / 100,
                        'discount': 0,
                        'tax_ids': [(6, 0, product.taxes_id.ids)]
                    }))
                for sub_item in item['subItems']:
                    sub_product = request.env['product.product'].sudo().search(
                        [('id', '=', int(item['plu'].split('-')[1]))],
                        limit=1)
                    order_lines.append((0, 0, {
                        'full_product_name': product.name,
                        'product_id': product.product_variant_id.id,
                        'price_unit': item['price'] / 100,
                        'qty': item['quantity'],
                        'price_subtotal': item['price'] * item['quantity'] / 100,
                        'price_subtotal_incl': item['price'] * item['quantity'] / 100,
                        'discount': 0,
                        'tax_ids': [(6, 0, product.taxes_id.ids)]
                    }))
                order_data = {
                    'config_id': pos_config.id,
                    'company_id': pos_config.company_id.id,
                    'note': data['note'],
                    'amount_paid': data['payment']['amount'] / 100,
                    'amount_return': 0.0,
                    'amount_tax': data['taxTotal'] / 100,
                    'amount_total': data['payment']['amount'] / 100,
                    'fiscal_position_id': False,
                    'pricelist_id': pos_config.pricelist_id.id,
                    'lines': order_lines,
                    'name': pos_reference,
                    'pos_reference': pos_reference,
                    'order_payment_type':str(data['payment']['type']),
                    'partner_id': self.find_partner(data['channel']),
                    'date_order': fields.Datetime.to_string(fields.Datetime.now()),
                    'session_id': pos_config.current_session_id.id,
                    'sequence_number': sequence_number,
                    'user_id': pos_config.current_user_id.id,
                    'is_online_order': True,
                    'online_order_id': data['_id'],
                    'floor': 'Online',
                    'online_order_status': 'approved' if is_auto_approve else 'open',
                    'order_type': str(data['orderType']),
                    'online_order_paid': data['orderIsAlreadyPaid'],
                    'channel_discount':data['discountTotal']/100,
                    'channel_service_charge':data['serviceCharge']/100,
                    'channel_delivery_charge':data['deliveryCost']/100,
                    'channel_tip_amount':data['tip']/100,
                    'channel_total_amount':data['payment']['amount'] / 100,
                    'delivery_note':data['deliveryNote'],
                }
            return order_data
        except Exception as e:
            _logger.error(f"Failed to create order data: {str(e)}")
            return False

    @http.route('/deliverect/pos/products/<int:pos_id>', type='http', methods=['GET'], auth="none", csrf=False)
    def sync_products(self, pos_id):
        """webhook for syncing products with deliverect"""
        try:
            product_data = self.generate_data(self, pos_id)
            return request.make_response(
                json.dumps(product_data),
                headers={'Content-Type': 'application/json'},
                status=200
            )
        except Exception as e:
            _logger.error(f"product sync error: {str(e)}")
            return request.make_response('', status=500)

    @http.route('/deliverect/pos/orders/<int:pos_id>', type='http', methods=['POST'], auth='none', csrf=False)
    def receive_pos_order(self, pos_id):
        """webhook for receiving pos orders from deliverect"""
        try:
            pos_config = request.env['pos.config'].sudo().browse(pos_id)
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
                pos_order_data = self.create_order_data(self, data, pos_id)
                if pos_order_data:
                    order = request.env['pos.order'].sudo().create(pos_order_data)
                    if data['orderIsAlreadyPaid']:
                        payment_context = {"active_ids": order.ids, "active_id": order.id}
                        order_payment = request.env['pos.make.payment'].with_user(pos_config.current_user_id.id).sudo(
                        ).with_context(
                            **payment_context).create({
                            'amount': order.amount_total,
                            'payment_method_id': deliverect_payment_method.id,
                        })
                        order_payment.with_context(**payment_context).check()
                    _logger.info(f"Trying to Generating order notification for pos")
                    self.generate_order_notification(pos_id)
                    return Response(
                        json.dumps({'status': 'success', 'message': 'Order created',
                                    'order_id': order.id}),
                        content_type='application/json',
                        status=200
                    )

        except Exception as e:
            _logger.error(f"Error processing order webhook: {str(e)}")
            return Response(
                json.dumps({
                    'status': 'error',
                    'message': f'Message: {e}',
                }),
                content_type='application/json',
                status=400
            )

    @http.route('/deliverect/pos/register/<int:pos_id>', type='http', methods=['POST'], auth="none", csrf=False)
    def register_pos(self, pos_id):
        """webhook for registering pos with deliverect"""
        pos_config = request.env['pos.config'].sudo().browse(pos_id)
        config_param = request.env['ir.config_parameter'].sudo()
        base_url = config_param.get_param('web.base.url')
        try:
            data = json.loads(request.httprequest.data)
            pos_config.write({
                'account_id': data.get('accountId'),
                'location_id': data.get('locationId'),
            })
            is_channel_present = request.env['pos.config'].sudo().browse(pos_id).create_customers_channel()
            request.env['deliverect.allergens'].sudo().update_allergens()
            if is_channel_present['params']['title'] == 'Failure':
                pos_config.write({
                    'status_message': f"{is_channel_present['params']['message']}",
                })
                return request.make_response(
                    json.dumps({'error': is_channel_present['params']['message']}),
                    headers=[('Content-Type', 'application/json')]
                )
            else:
                pos_config.write({
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

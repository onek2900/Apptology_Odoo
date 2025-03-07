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
                'name': f"DELIVERECT-CUST",
                'channel_id': channel_id,
            })
        return partner.id

    @staticmethod
    def image_upload(self, product_tmpl_id, template=True):
        """function for uploading product image to deliverect"""
        model = 'product.template'
        image = 'image_1920'
        if not template:
            model = 'product.product'
            image = 'image_variant_1920'
        attachment_id = request.env['ir.attachment'].sudo().search(
            domain=[('res_model', '=', model),
                    ('res_id', '=', product_tmpl_id),
                    ('res_field', '=', image)]
        )
        product_image_url = False
        if attachment_id:
            attachment_id.write({'public': True})
            base_url = request.env['ir.config_parameter'].sudo().get_param(
                'web.base.url')
            product_image_url = f"{base_url}{attachment_id.image_src}.jpg"
        return product_image_url

    @staticmethod
    def create_combo_product_data(self, combo_product):
        """function for creating combo product data for deliverect"""
        deliverect_products = []
        main_product = {
            "productType": 1,
            "isCombo": True,
            "plu": f"P-{combo_product.id}",
            "price": 0,
            "name": combo_product.name,
            "imageUrl": self.image_upload(self, combo_product.product_tmpl_id.id),
            "subProducts": []
        }
        sum_base_price = sum(combo_product.combo_ids.mapped('base_price'))
        for combo in combo_product.combo_ids:
            modifier_group_plu = f"CC-{combo.id}"
            main_product["subProducts"].append(modifier_group_plu)
            modifier_group = {
                "productType": 3,
                "plu": modifier_group_plu,
                "name": combo.name,
                "subProducts": [],
            }
            base_price = combo.base_price
            for line in combo.combo_line_ids:
                product = line.product_id
                product_tax = request.env['product.product'].sudo().browse(product.id).taxes_id.amount
                modifier_plu = f"PM-{product.id}"
                modifier_group["subProducts"].append(modifier_plu)
                modifier = {
                    "productType": 2,
                    "plu": modifier_plu,
                    "price": round((((base_price / sum_base_price) * combo_product.lst_price) + line.combo_price), 2
                                   ) * 100,
                    "name": product.name,
                    "imageUrl": self.image_upload(self, product.product_tmpl_id.id),
                    "deliveryTax": product_tax * 1000,
                    "takeawayTax": product_tax * 1000,
                    "eatInTax": product_tax * 1000,
                }
                deliverect_products.append(modifier)
            deliverect_products.append(modifier_group)
        deliverect_products.insert(0, main_product)
        return deliverect_products

    @staticmethod
    def create_product_data(self):
        """function for creating product data for deliverect"""
        products = request.env['product.product'].sudo().search([('active', '=', True),
                                                                 ('detailed_type', '!=', 'combo'),
                                                                 ('attribute_line_ids', '=', False),
                                                                 ('available_in_pos', '=', True)])
        return products.mapped(lambda product: {
            "name": product.name,
            "plu": f"P-{product.id}",
            "price": int(product.lst_price * 100),
            "productType": 1,
            "deliveryTax": product.taxes_id.amount * 1000,
            "takeawayTax": product.taxes_id.amount * 1000,
            "eatInTax": product.taxes_id.amount * 1000,
            "imageUrl": self.image_upload(self, product.product_tmpl_id.id),
        })

    @staticmethod
    def generate_order_notification(pos_id):
        """function for generating notification for pos order"""
        channel = f"new_pos_order_{pos_id}"
        request.env["bus.bus"]._sendone(channel, "notification", {
            "channel": channel,
        })

    @staticmethod
    def generate_data(self, pos_id):
        """function for generating data for pos order"""
        pos_config = request.env['pos.config'].sudo().browse(pos_id)
        product_data = self.create_product_data(self)
        combo_products = request.env['product.product'].sudo().search([('detailed_type', '=', 'combo')])
        for combo in combo_products:
            product_data += self.create_combo_product_data(self, combo)
        pos_categories = request.env['pos.category'].sudo().search([]).mapped(
            lambda category: {
                "name": category.name,
                "posCategoryId": category.id,
            })
        account_id = pos_config.account_id
        location_id = pos_config.location_id
        return {
            "priceLevels": [],
            'categories': pos_categories,
            'products': product_data,
            "accountId": account_id,
            "locationId": location_id
        }

    @staticmethod
    def generate_pos_reference(self, channel_order_id, channel_id):
        """function for generating sequence number for pos order"""
        numeric_part = ''.join(filter(str.isdigit, channel_order_id))
        last_7_digits = numeric_part[-7:].zfill(7)
        pos_reference = f"Online-Order {int(channel_id):05d}-{last_7_digits[:3]}-{last_7_digits[3:]}"
        return pos_reference

    @staticmethod
    def create_order_data(self, data, pos_id):
        """function for pos order data from deliverect data"""
        pos_reference = self.generate_pos_reference(self, data['channelOrderId'], data['channel'])
        pos_config = request.env['pos.config'].sudo().browse(pos_id)
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
            order_lines = []
            for item in data['items']:
                if item.get("isCombo"):
                    for subitem in item['subItems']:
                        product = request.env['product.product'].sudo().search(
                            [('id', '=', int(subitem['plu'].split('-')[1]))],
                            limit=1)
                        order_lines.append((0, 0, {
                            'full_product_name': product.name,
                            'is_cooking': True,
                            'product_id': product.product_variant_id.id,
                            'price_unit': subitem['price'] / 100,
                            'qty': subitem['quantity'],
                            'price_subtotal': subitem['price'] * subitem['quantity'] / 100,
                            'price_subtotal_incl': subitem['price'] * subitem['quantity'] / 100,
                            'discount': 0,
                        }))
                else:
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
            deliverect_payment_method = request.env.ref("apptology_deliverect.pos_payment_method_deliverect")
            order_data = {'data':
                              {'to_invoice': True,
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
                               'partner_id': self.find_partner(data['channel']),
                               'date_order': fields.Datetime.to_string(fields.Datetime.now()),
                               'pos_session_id': pos_config.current_session_id.id,
                               'sequence_number': sequence_number,
                               'statement_ids': [[0,
                                                  0,
                                                  {'amount': data['payment']['amount'] / 100,
                                                   'name': fields.Datetime.now(),
                                                   'payment_method_id': deliverect_payment_method.id}]],
                               'user_id': pos_config.current_user_id.id},
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
            data = json.loads(request.httprequest.data)
            if data['status'] == 100 and data['_id']:
                order = request.env['pos.order'].sudo().search([('online_order_id', '=', data['_id'])], limit=1)
                order.write({
                    'order_status': 'cancel',
                    'online_order_status': 'cancelled',
                    'declined_time': fields.Datetime.now()
                })
                deliverect_payment_method = request.env.ref("apptology_deliverect.pos_payment_method_deliverect")
                refund_action = order.refund()
                refund = request.env['pos.order'].sudo().browse(refund_action['res_id'])
                payment_context = {"active_ids": refund.ids, "active_id": refund.id}
                refund_payment = request.env['pos.make.payment'].sudo().with_context(**payment_context).create({
                    'amount': refund.amount_total,
                    'payment_method_id': deliverect_payment_method.id,
                })
                refund_payment.with_context(**payment_context).check()
                request.env['pos.order'].with_user(pos_config.current_user_id.id).browse(
                    refund.id).action_pos_order_invoice()
            else:
                pos_order_data = self.create_order_data(self, data, pos_id)
                if pos_order_data:
                    is_auto_approve = pos_config.auto_approve
                    order = request.env['pos.order'].with_user(pos_order_data['data']['user_id']).create_from_ui(
                        [pos_order_data])
                    order = request.env['pos.order'].sudo().browse(order[0]['id'])
                    order.write({
                        'is_online_order': True,
                        'online_order_id': data['_id'],
                        'floor': 'Online',
                        'online_order_status': 'approved' if is_auto_approve else 'open',
                        'order_type': str(data['orderType']),
                    })
                    self.generate_order_notification(pos_id)
                    return Response(
                        json.dumps({'status': 'success', 'message': 'Order created',
                                    'order_id': order.id}),
                        content_type='application/json',
                        status=200
                    )
                else:
                    raise Exception("Sequence not found for POS")
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

    @http.route('/deliverect/pos/register/<int:pos_id>', type='json', methods=['POST'], auth="none", csrf=False)
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
            if is_channel_present['params']['title'] == 'Failure':
                pos_config.write({
                    'status_message': f"{is_channel_present['params']['message']}",
                })
            else:
                pos_config.write({
                    'status_message': f"POS Registration Successful"
                })
                return {
                    "ordersWebhookURL": f"{base_url}/deliverect/pos/orders/{pos_id}",
                    "syncProductsURL": f"{base_url}/deliverect/pos/products/{pos_id}"
                }

        except Exception as e:
            _logger.error(f"Registration error: {str(e)}")

from odoo import http, _, fields, Command
from odoo.http import request, Response
import json
import logging
import re

_logger = logging.getLogger(__name__)


class DeliverectWebhooks(http.Controller):
    """Controller for handling Deliverect webhooks and API integration."""

    @staticmethod
    def find_partner(channel_id):
        channel = request.env['deliverect.channel'].sudo().search([('channel_id', '=', channel_id)],
                                                                  limit=1)
        partner = request.env['res.partner'].sudo().search([('channel_id', '=', channel_id)])
        if not partner:
            partner = request.env['res.partner'].sudo().create({
                'name': channel['name'],
                'channel_id': channel_id
            })
        return partner.id

    @staticmethod
    def image_upload(self, product_tmpl_id, template=True):
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
        deliverect_products = []

        # Convert main combo product (Type 1)
        main_product = {
            "productType": 1,
            "isCombo": True,
            "plu": f"P-{combo_product.id}",
            "price": 0,
            "name": combo_product.name,
            "imageUrl": self.image_upload(self, combo_product.product_tmpl_id.id),
            "subProducts": []
        }
        # Process combo attributes (Type 3 - modifier groups)
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

            # Process combo lines (Type 2 - modifiers)
            for line in combo.combo_line_ids:
                product = line.product_id
                product_tax = request.env['product.product'].sudo().browse(product.id).taxes_id.amount
                modifier_plu = f"PM-{product.id}"
                modifier_group["subProducts"].append(modifier_plu)
                modifier = {
                    "productType": 2,
                    "plu": modifier_plu,
                    "price": round((((base_price / sum_base_price) * combo_product.lst_price) + line.combo_price),2
                                   ) * 100,
                    "name": product.name,
                    "imageUrl": self.image_upload(self, product.product_tmpl_id.id),
                    "deliveryTax": product_tax*1000,
                    "takeawayTax": product_tax*1000,
                    "eatInTax": product_tax*1000,
                }
                deliverect_products.append(modifier)
            deliverect_products.append(modifier_group)
        deliverect_products.insert(0, main_product)
        return deliverect_products

    @staticmethod
    def create_product_data(self):
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
    def generate_order_notification(pos_ref):
        channel = "new_pos_order"
        request.env["bus.bus"]._sendone(channel, "notification", {
            "channel": channel,
            "pos_ref": pos_ref
        })

    @staticmethod
    def generate_data(self):
        product_data = self.create_product_data(self)
        combo_products = request.env['product.product'].sudo().search([('detailed_type', '=', 'combo')])
        variant_products = request.env['product.template'].sudo().search([('attribute_line_ids', '!=', False),
                                                                          ('product_variant_ids.product_template_variant_value_ids','!=',False)])
        for combo in combo_products:
            product_data += self.create_combo_product_data(self, combo)

        pos_categories = request.env['pos.category'].sudo().search([]).mapped(
            lambda category: {
                "name": category.name,
                "posCategoryId": category.id,
            })
        config_parameter = request.env['ir.config_parameter'].sudo()
        account_id = config_parameter.get_param('account_id')
        location_id = config_parameter.get_param('location_id')
        return {
            "priceLevels": [],
            'categories': pos_categories,
            'products': product_data,
            "accountId": account_id,
            "locationId": location_id
        }

    @staticmethod
    def generate_sequence_number(self, channel_order_id, channel_id):
        # Format: Order-xxxxx-xxx-xxxx
        numeric_part = ''.join(filter(str.isdigit, channel_order_id))
        last_7_digits = numeric_part[-7:].zfill(7)
        pos_reference = f"Order-{int(channel_id):05d}-{last_7_digits[:3]}-{last_7_digits[3:]}"
        return pos_reference

    @staticmethod
    def create_order_data(self, data):
        current_session = request.env['pos.session'].sudo().search([
            ('state', 'in', ['opened'])], limit=1)
        pos_reference = self.generate_sequence_number(self, data['channelOrderId'], data['channel'])
        pos_config = current_session.config_id
        ir_sequence_session = pos_config.env['ir.sequence'].with_context(
            company_id=pos_config.company_id.id).next_by_code(f'pos.order_{pos_config.current_session_id.id}')
        sequence_number = re.findall(r'\d+', ir_sequence_session)[0]
        is_auto_approve = pos_config.auto_approve
        print('is auto approve :',is_auto_approve)
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
                product = request.env['product.product'].sudo().search([('id', '=', int(item['plu'].split('-')[1]))],
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

        order_data = {
            'company_id': request.env.company.id,
            'sequence_number': sequence_number,
            'partner_id': self.find_partner(data['channel']),
            'session_id': pos_config.current_session_id.id,
            'pricelist_id': pos_config.pricelist_id.id,
            'lines': order_lines,
            'amount_total': data['payment']['amount'] / 100,
            'amount_tax': data['taxTotal'] / 100,
            'amount_paid': data['payment']['amount'] / 100,
            'amount_return': 0.0,
            'to_invoice': True,
            'pos_reference': pos_reference,
            'online_order_id': data['_id'],
            'date_order': fields.Datetime.to_string(fields.Datetime.now()),
            'user_id': request.env.uid,
            'order_type': str(data['orderType']),
            'online_order_status': 'approved' if is_auto_approve else 'open',
            'is_online_order': True,
            'note': data['note'],
            'floor': 'Online'
        }
        return order_data

    @http.route('/deliverect/pos/products', type='http', methods=['GET'], auth="none", csrf=False)
    def sync_products(self):
        try:
            product_data = self.generate_data(self)
            return request.make_response(
                json.dumps(product_data),
                headers={'Content-Type': 'application/json'},
                status=200
            )
        except Exception as e:
            _logger.error(f"product sync error: {str(e)}")
            return request.make_response('', status=500)

    @http.route('/deliverect/pos/orders', type='http', methods=['POST'], auth='public', csrf=False)
    def receive_pos_order(self):
        try:
            data = json.loads(request.httprequest.data)
            if data['status'] == 100 and data['_id']:
                print('cancelling order')
                order = request.env['pos.order'].sudo().search([('online_order_id', '=', data['_id'])], limit=1)
                order.write({
                    'order_status': 'cancel',
                    'online_order_status':'cancelled',
                    'declined_time': fields.Datetime.now()
                })
                deliverect_payment_method = request.env.ref("apptology_deliverect.pos_payment_method_deliverect")
                refund_action = order.refund()
                refund = request.env['pos.order'].sudo().browse(refund_action['res_id'])
                payment_context = {"active_ids": [refund.id], "active_id": refund.id}
                refund_payment = request.env['pos.make.payment'].sudo().with_context(**payment_context).create({
                    'amount': refund.amount_total,
                    'payment_method_id': deliverect_payment_method.id,
                })
                refund_payment.with_context(**payment_context).check()
                order.action_pos_order_invoice()
            else:
                pos_order_data = self.create_order_data(self, data)
                deliverect_payment_method = request.env.ref("apptology_deliverect.pos_payment_method_deliverect")
                order = request.env['pos.order'].sudo().create(pos_order_data)
                payment_context = {"active_ids": [order.id], "active_id": order.id}
                order_payment = request.env['pos.make.payment'].sudo().with_context(**payment_context).create({
                    'amount': order.amount_total,
                    'payment_method_id': deliverect_payment_method.id
                })
                order_payment.with_context(**payment_context).check()
                self.generate_order_notification(pos_order_data['pos_reference'])
                return Response(
                    json.dumps({'status': 'success', 'message': 'Order created',
                                'order_id': order.id}),
                    content_type='application/json',
                    status=200
                )
        except Exception as e:
            _logger.error(f"Error processing order webhook: {str(e)}")
            return Response(
                json.dumps({'status': 'error', 'message': str(e)}),
                content_type='application/json',
                status=200
            )

    @http.route('/deliverect/pos/register', type='json', methods=['POST'], auth="none", csrf=False)
    def register_pos(self):
        config_param = request.env['ir.config_parameter'].sudo()
        base_url = config_param.get_param('web.base.url')
        try:
            data = json.loads(request.httprequest.data)
            config_param.set_param('account_id', data.get('accountId'))
            config_param.set_param('location_id', data.get('locationId'))
            request.env['deliverect.channel'].sudo().update_channel()
            request.env['deliverect.allergens'].sudo().update_allergens()
            return {
                "ordersWebhookURL": f"{base_url}/deliverect/pos/orders",
                "syncProductsURL": f"{base_url}/deliverect/pos/products?locationID={data.get('locationId')}"
            }
        except Exception as e:
            _logger.error(f"Registration error: {str(e)}")

from odoo import http, _, fields
from odoo.http import request, Response
import json
import logging

_logger = logging.getLogger(__name__)


class DeliverectWebhooks(http.Controller):
    """Controller for handling Deliverect webhooks and API integration."""

    @staticmethod
    def create_or_get_partner(customer_data):
        partner = request.env['res.partner'].sudo().search([('email', '=', customer_data['email'])],
                                                           limit=1)
        if not partner:
            partner = request.env['res.partner'].sudo().create({
                'name': customer_data['name'],
                'email': customer_data['email'],
                'company_name': customer_data['companyName'],
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
    def create_variant_product_data(self, template):
        # TODO Only considering one attribute for variant product
        product_data = []
        main_product = {
            "productType": 1,
            "plu": f"PT-{template.id}",
            "price": 0,
            "name": template.name,
            "imageUrl": self.image_upload(self, template.id),
            "isVariant": True,
            "subProducts": []
        }
        attribute = template.attribute_line_ids[0]
        attribute_variants = {
            "productType": 3,
            "plu": f"ATT-{attribute.attribute_id.id}",
            "name": f"{attribute.attribute_id.name}",
            "isVariantGroup": True,
            "subProducts": [],
        }
        for variant in template.product_variant_ids:
            variant_data = {
                "productType": 1,
                "plu": f"PP-{variant.id}",
                "price": int(variant.lst_price * 100),
                "name": f"{variant.name}-{variant.product_template_variant_value_ids[0].name}",
                "imageUrl": self.image_upload(self, variant.id, False),
            }
            attribute_variants["subProducts"].append(variant_data["plu"])
            product_data.append(variant_data)
        main_product["subProducts"].append(attribute_variants["plu"])
        product_data.append(attribute_variants)
        product_data.append(main_product)
        return product_data

    @staticmethod
    def create_combo_product_data(self, combo_product):
        deliverect_products = []

        # Convert main combo product (Type 1)
        main_product = {
            "productType": 1,
            "isCombo": True,
            "plu": f"PT-{combo_product.id}",
            "price": int(combo_product.list_price * 100),
            "name": combo_product.name,
            "imageUrl": self.image_upload(self, combo_product.id),
            "subProducts": []
        }

        # Process combo attributes (Type 3 - modifier groups)
        for combo in combo_product.combo_ids:
            modifier_group_plu = f"CC-{combo.id}"
            main_product["subProducts"].append(modifier_group_plu)
            modifier_group = {
                "productType": 3,
                "plu": modifier_group_plu,
                "name": combo.name,
                "subProducts": [],
            }

            # Process combo lines (Type 2 - modifiers)
            for line in combo.combo_line_ids:
                product_tax = request.env['product.product'].sudo().browse(line.id).taxes_id.amount * 1000
                product = line.product_id
                modifier_plu = f"PM-{product.product_tmpl_id.id}"
                modifier_group["subProducts"].append(modifier_plu)
                modifier = {
                    "productType": 2,
                    "plu": modifier_plu,
                    "price": line.combo_price * 100,
                    "name": product.name,
                    "imageUrl": self.image_upload(self, product.product_tmpl_id.id),
                    "deliveryTax": product_tax,
                    "takeawayTax": product_tax,
                    "eatInTax": product_tax,
                }
                deliverect_products.append(modifier)
            deliverect_products.append(modifier_group)
        deliverect_products.insert(0, main_product)
        return deliverect_products

    @staticmethod
    def create_product_data(self):
        products = request.env['product.template'].sudo().search([('active', '=', True),
                                                                  ('detailed_type', '!=', 'combo'),
                                                                  ('attribute_line_ids', '=', False),
                                                                  ('available_in_pos', '=', True)])
        return products.mapped(lambda product: {
            "name": product.name,
            "plu": f"PT-{product.id}",
            "price": int(product.list_price * 100),
            "productType": 1,
            "deliveryTax": product.taxes_id.amount * 1000,
            "takeawayTax": product.taxes_id.amount * 1000,
            "eatInTax": product.taxes_id.amount * 1000,
            "imageUrl": self.image_upload(self, product.id),
        })

    @staticmethod
    def generate_data(self):
        product_data = self.create_product_data(self)
        combo_products = request.env['product.template'].sudo().search([('detailed_type', '=', 'combo')])
        variant_templates = request.env['product.template'].sudo().search([('attribute_line_ids', '!=', False)])
        for combo in combo_products:
            product_data += self.create_combo_product_data(self, combo)
        for template in variant_templates:
            product_data += self.create_variant_product_data(self, template)

        pos_categories = request.env['pos.category'].sudo().search([]).mapped(
            lambda category: {
                "name": category.name,
                "posCategoryId": category.id,
            })
        return {
            "priceLevels": [],
            'categories': pos_categories,
            'products': product_data,
            "accountId": "67a075460cfd6d82d1f09e30",
            "locationId": "67a075480cfd6d82d1f09e35"
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
        channel_order_id = data['channelOrderId']
        channel_id = data['channel']
        pos_reference = self.generate_sequence_number(self, channel_order_id, channel_id)
        pos_config = request.env['pos.config'].sudo().search([('name', '=', 'Restaurant')], limit=1)
        config_id=pos_config.id
        pos_session = request.env['pos.session'].sudo().search([
            ('config_id', '=', config_id),
            ('state', '=', 'opened')
        ], limit=1)
        is_auto_approve = request.env['ir.config_parameter'].sudo().get_param('automatic_approval')
        order_lines = []
        print('data :', data)

        for item in data['items']:
            product = request.env['product.product'].sudo().search([('id', '=', int(item['plu'].split('-')[1]))],
                                                                   limit=1)
            if product:
                order_lines.append((0, 0, {
                    'full_product_name': product.name,
                    'is_cooking': True,
                    'product_id': product.product_variant_id.id,
                    'price_unit': item['price'] / 100,
                    'qty': item['quantity'],
                    'price_subtotal': item['price'] * item['quantity'] / 100,
                    'price_subtotal_incl': item['price'] * item['quantity'] / 100,
                    'discount': 0,
                    'tax_ids': [(6, 0, product.taxes_id.ids)]
                }))
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
        print('ORDER LINES :',order_lines)
        order_data = {
                           'online_order_id': data['_id'],
                           'to_invoice': True,
                           'amount_paid': data['payment']['amount'] / 100,
                           'amount_return': 0.0,
                           'amount_tax': data['taxTotal'] / 100,
                           'amount_total': data['payment']['amount'] / 100,
                           'date_order': fields.Datetime.to_string(fields.Datetime.now()),
                           'fiscal_position_id': False,
                           'pricelist_id': pos_config.pricelist_id.id,
                           'lines': order_lines,
                           'name': f"Online/{data['channelOrderDisplayId']}",
                           'partner_id': self.create_or_get_partner(data['customer']),
                           'session_id': pos_config.current_session_id.id,
                           'sequence_number': 2,
                           'user_id': request.env.uid,
                           'pos_reference': pos_reference,
                           'company_id': request.env.company.id,
                           'order_type': str(data['orderType']),
                           'online_order_status': 'approved' if is_auto_approve else 'open',
                           'is_online_order': True,
                           'note': data['note'],
                           'to_invoice': True,
                           'is_cooking': True,
                           'floor': 'Online'}
        return order_data



    @http.route('/deliverect/pos/products', type='http', methods=['GET'], auth="none", csrf=False)
    def sync_products(self):
        print('inside product sync')
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
        print('***ORDER RECEIVED***')
        try:
            data = json.loads(request.httprequest.data)
            if data['status'] == 100 and data['_id']:
                order = request.env['pos.order'].sudo().search([('online_order_id', '=', data['_id'])], limit=1)
                order.write({
                    'online_order_status': 'cancelled',
                    'state': 'cancel',
                    'order_status': 'cancel',
                    'declined_time': fields.Datetime.now(),
                })
            else:
                print('***TRYING TO CREATE ORDER***')
                pos_order_data = self.create_order_data(self, data)
                print('ORDER DATA :', pos_order_data)

                order = request.env['pos.order'].sudo().create(pos_order_data)

                payment_context = {"active_ids": [order.id], "active_id": order.id}
                order_payment = request.env['pos.make.payment'].sudo().with_context(**payment_context).create({
                    'amount': order.amount_total,
                    'payment_method_id': 2
                })
                order_payment.with_context(**payment_context).check()
                print('check worked')
                print('order created :',request.env['pos.order'].sudo().browse(order['id']))
                channel = "new_pos_order"
                request.env["bus.bus"]._sendone(channel, "notification", {
                    "message": "New Order Received"
                })
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
            return {
                "ordersWebhookURL": f"{base_url}/deliverect/pos/orders",
                "syncProductsURL": f"{base_url}/deliverect/pos/products?locationID={data.get('locationId')}"
            }
        except Exception as e:
            _logger.error(f"Registration error: {str(e)}")

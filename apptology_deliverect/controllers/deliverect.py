from odoo import http, _
from odoo.http import request, Response
import json
import logging

_logger = logging.getLogger(__name__)

import time

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
    def image_upload(self, product_tmpl_id):
        attachment_id = request.env['ir.attachment'].sudo().search(
            domain=[('res_model', '=', 'product.template'),
                    ('res_id', '=', product_tmpl_id),
                    ('res_field', '=', 'image_1920')]
        )
        print('attachment id :', attachment_id)
        product_image_url = False
        if attachment_id:
            attachment_id.write({'public': True})
            base_url = request.env['ir.config_parameter'].sudo().get_param(
                'web.base.url')
            product_image_url = f"{base_url}{attachment_id.image_src}.jpg"
        return product_image_url

    @staticmethod
    def convert_combo(combo_product):
        deliverect_products = []

        # Convert main combo product (Type 1)
        main_product = {
            "productType": 1,
            "plu": f"COMBO-{combo_product.id}",
            "price": int(combo_product.list_price * 100),
            "name": combo_product.name,
            "subProducts": []
        }

        # Process combo attributes (Type 3 - modifier groups)
        for combo in combo_product.combo_ids:
            modifier_group_plu = f"COPT-{combo.id}"
            main_product["subProducts"].append(modifier_group_plu)

            modifier_group = {
                "productType": 3,
                "plu": modifier_group_plu,
                "name": combo.name,
                "subProducts": [],
            }

            # Process combo lines (Type 2 - modifiers)
            for line in combo.combo_line_ids:
                product = line.product_id
                modifier_plu = f"CPRO-{product.id}"
                modifier_group["subProducts"].append(modifier_plu)

                modifier = {
                    "productType": 2,
                    "plu": modifier_plu,
                    "price": 123,
                    "name": product.name,
                }
                deliverect_products.append(modifier)

            deliverect_products.append(modifier_group)

        deliverect_products.insert(0, main_product)
        return deliverect_products



    @staticmethod
    def create_product_data(self):
        # for rec in request.env['product.template'].sudo().browse(67).combo_ids:
        #     print(rec.combo_line_ids.read())

        products = request.env['product.template'].sudo().search([('active', '=', True),
                                                                  ('detailed_type','!=','combo'),
                                                                  ('is_product_variant','=',False),
                                                                  ('attribute_line_ids','=',False),
                                                                 ('available_in_pos', '=', True)])
        print('normal :',products)
        pos_categories = request.env['pos.category'].sudo().search([]).mapped(
            lambda category: {
                "name": category.name,
                "posCategoryId": category.id
            })
        product_data = products.mapped(lambda product: {
            "name": product.name,
            "plu": f"P-{product.id}",
            "price": int(product.list_price*100),
            "imageUrl": self.image_upload(self,product.id),
        })
        combo_products=request.env['product.template'].sudo().search([('detailed_type','=','combo')])
        print('combo :',combo_products)
        for combo in combo_products:
            data = self.convert_combo(combo)
            product_data+=data
        print('final product data :')

        return {
            "priceLevels": [],
            'categories': pos_categories,
            'products': product_data,
            "accountId": "67a075460cfd6d82d1f09e30",
            "locationId": "67a075480cfd6d82d1f09e35"
        }

    @staticmethod
    def create_order_data(self, data):
        print('create order data function')
        # Format: Order-xxxxx-xxx-xxxx
        channel_order_id=data['channelOrderId']
        numeric_part = ''.join(filter(str.isdigit, channel_order_id))
        last_7_digits = numeric_part[-7:].zfill(7)
        channel_id=data['channel']
        pos_reference = f"Order-{int(channel_id):05d}-{last_7_digits[:3]}-{last_7_digits[3:]}"
        config_id = request.env['pos.config'].sudo().search([('name', '=', 'Restaurant')], limit=1).id
        pos_session = request.env['pos.session'].sudo().search([
            ('config_id', '=', config_id),
            ('state', '=', 'opened')
        ], limit=1)
        is_auto_approve=request.env['ir.config_parameter'].sudo().get_param('automatic_approval')
        order_lines = []
        for item in data['items']:
            product = request.env['product.product'].sudo().search([('id', '=', int(item['plu'].split('-')[1]))],
            limit=1)
            print('product found :',product)
            if product:
                order_lines.append((0, 0, {
                    'full_product_name': product.name,
                    'is_cooking':True,
                    'product_id': product.id,
                    'price_unit': item['price']/100,
                    'qty': item['quantity'],
                    'price_subtotal': item['price'] * item['quantity']/100,
                    'price_subtotal_incl': item['price'] * item['quantity']/100,
                    'discount': 0,
                }))

        return {
            'online_order_id':data['_id'],
            'user_id': 2,
            'company_id': request.env.company.id,
            'session_id': pos_session.id,
            'partner_id': self.create_or_get_partner(data['customer']),
            'lines': order_lines,
            'order_type':str(data['orderType']),
            'amount_paid': data['payment']['amount']/100,
            'amount_total': data['payment']['amount']/100,
            'amount_tax': data['taxTotal']/100,
            'amount_return': 0.0,
            'online_order_status':'approved' if is_auto_approve else 'open',
            'is_online_order':True,
            'pos_reference': pos_reference,
            'name': f"Online/{data['channelOrderDisplayId']}",
            'note': data['note'],
            'last_order_preparation_change': '{}',
            'to_invoice': True,
            'is_cooking':True,
            'floor':'Online'
        }

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

    @http.route('/deliverect/pos/products', type='http', methods=['GET'], auth="none", csrf=False)
    def sync_products(self):
        print('inside product sync')
        try:
            product_data = self.create_product_data(self)
            print('product data')
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
        print('***ORDER UPDATE***')
        try:
            data = json.loads(request.httprequest.data)
            print('data :',data)
            if data['status']==100 and data['_id']:
                print('***ORDER CANCELLED***',data['_id'])
                order = request.env['pos.order'].sudo().search([('online_order_id', '=', data['_id'])],limit=1)
                print('order :',order)
                order.write({
                    'online_order_status': 'cancelled',
                    'state':'cancel'
                })
            else:
                print('***ORDER CREATED***')
                pos_order_data = self.create_order_data(self, data)
                print('pos order data :',pos_order_data)
                order = request.env['pos.order'].sudo().create(pos_order_data)
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

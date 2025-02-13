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
    def create_product_data():
        products = request.env['product.product'].sudo().search([('active', '=', True),
                                                                 ('available_in_pos', '=', True)])
        pos_categories = request.env['pos.category'].sudo().search([]).mapped(
            lambda category: {
                "name": category.name,
                "posCategoryId": category.id
            })
        product_data = products.mapped(lambda product: {
            "name": product.name,
            "plu": product.default_code or f'SKU-{product.id}',
            "price": product.list_price,
            "deliveryTax": 11,
            "visible": product.all_channel_visible,
            "posCategoryIds": [str(cat.id) for cat in product.pos_categ_ids] if product.pos_categ_ids else [],
            "imageUrl": f"/web/image/product.product/{product.id}/image_1024" if product.image_1920 else ""
        })
        return {
            "priceLevels": [],
            'categories': pos_categories,
            'products': product_data,
            "accountId": "67a075460cfd6d82d1f09e30",
            "locationId": "67a075480cfd6d82d1f09e35"
        }

    @staticmethod
    def create_order_data(self, data):
        number = data['channelOrderId'].replace('T', '')
        # Format: Order-xxxxx-xxx-xxxx
        sequence = "00009"
        branch = number[-7:-4].zfill(3)
        order_num = number[-4:].zfill(4)
        pos_reference = f"Order-{sequence}-{branch}-{order_num}"
        pos_config = request.env['pos.config'].sudo().search([], limit=1)
        pos_session = pos_config.current_session_id
        is_auto_approve=request.env['ir.config_parameter'].sudo().get_param('automatic_approval')
        order_lines = []
        for item in data['items']:
            product = request.env['product.product'].sudo().search([('default_code', '=', item['plu'])], limit=1)
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
            'name': data['channelOrderDisplayId'],
            'note': data['note'],
            'last_order_preparation_change': '{}',
            'to_invoice': True,
            'order_status':'draft',
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
        try:
            product_data = self.create_product_data()
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
            print('pos order webhook')
            data = json.loads(request.httprequest.data)
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

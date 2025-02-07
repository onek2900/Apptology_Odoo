from odoo import http, _
from odoo.http import request,Response
import json
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)


class DeliverectWebhooks(http.Controller):
    """Controller for handling Deliverect webhooks and API integration."""

    @http.route('/deliverect/pos/register', type='json', methods=['POST'],
                auth="none", csrf=False)
    def register_pos(self):
        """Handle POS registration webhook."""
        base_url = request.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        try:
            data = json.loads(request.httprequest.data)
            request.env['deliverect.configuration'].sudo().search([],
                                                                  limit=1).write(
                {
                    'account_id': data.get('accountId'),
                    'location_id': data.get('locationId')
                })
            urls = {
                "ordersWebhookURL": f"{base_url}/deliverect/pos/orders",
                "syncProductsURL": f"{base_url}/deliverect/pos/products?locationID={data.get('locationId')}"
            }
            print(urls)
            return urls

        except Exception as e:
            _logger.error(f"Registration error: {str(e)}")

    def create_product_data(self):
        products_to_sync = request.env['product.product'].sudo().search(
            [('active', '=', True), ('available_in_pos', '=', True)],limit=15)
        pos_categories= request.env['pos.category'].sudo().search([]).mapped(lambda p:{
            "name":p.name,
            "posCategoryId":p.id
        })
        print(pos_categories)
        product_data = products_to_sync.mapped(lambda p: {
            "name": p.name,
            "plu": p.default_code or f'SKU-{p.id}',
            "price": p.list_price,
            "deliveryTax": 11
        })
        print(product_data)
        return {
            "priceLevels": [],
            'categories': pos_categories,
            'products': product_data,
            "accountId": "67a075460cfd6d82d1f09e30",
            "locationId": "67a075480cfd6d82d1f09e35"
        }


    @http.route('/deliverect/pos/products', type='http', methods=['GET'],
                auth="none", csrf=False)
    def sync_products(self, **kwargs):
        print(kwargs, 'teaster')
        try:
            product_data = self.create_product_data()
            print(product_data)
            return request.make_response(
                json.dumps(product_data),
                headers={'Content-Type': 'application/json'},
                status=200
            )
        except Exception as e:
            _logger.error(f"Async product sync error: {str(e)}")
            return request.make_response('', status=500)


    # @http.route('/deliverect/pos/orders', type='json', auth='none',
    #             methods=['POST'], csrf=False)
    # def receive_pos_order(self):
    #     """Handle incoming POS orders from Deliverect webhook."""
    #     print('order received :')
    #     try:
    #         # Get the raw data from the request
    #         data = json.loads(request.httprequest.data)
    #         print('data :',data)
    #         # Log the incoming order data for debugging
    #         _logger.info(f"Received order webhook data: {data}")
    #         return {
    #             'status': 'success',
    #             'message': 'Order received successfully'
    #         }
    #
    #     except Exception as e:
    #         # Log the error but still return a 200 response to prevent retries
    #         _logger.error(f"Error processing order webhook: {str(e)}")
    #         return {
    #             'status': 'success',
    #             'message': 'Order received'
    #         }

    @http.route(['/deliverect/pos/orders'], type='http', auth='public',
                methods=['POST'], csrf=False)
    def receive_pos_order(self, **kwargs):
        try:
            data = json.loads(request.httprequest.data)

            # Get POS config and session
            pos_config = request.env['pos.config'].sudo().search([], limit=1)
            pos_session = pos_config.current_session_id or request.env[
                'pos.session'].sudo().create({
                'user_id': request.env.ref('base.user_admin').id,
                'config_id': pos_config.id
            })

            # Create order lines
            order_lines = []
            for item in data['items']:
                product = request.env['product.product'].sudo().search(
                    [('default_code', '=', item['plu'])], limit=1)
                if product:
                    order_lines.append((0, 0, {
                        'product_id': product.id,
                        'price_unit': item['price'],
                        'qty': item['quantity'],
                        'price_subtotal': item['price'] * item['quantity'],
                        'price_subtotal_incl': item['price'] * item['quantity'],
                        'discount': 0,
                    }))

            pos_order_data = {
                'company_id': request.env.company.id,
                'session_id': pos_session.id,
                'partner_id': self._create_or_get_partner(data['customer']),
                'lines': order_lines,
                'amount_paid': data['payment']['amount'],
                'amount_total': data['payment']['amount'],
                'amount_tax': data['taxTotal'],
                'amount_return': 0.0,
                'pos_reference': data['channelOrderId'],
                'name': data['channelOrderDisplayId'],
                'note': data['note'],
                'last_order_preparation_change': '{}',
                'to_invoice': True
            }

            order = request.env['pos.order'].sudo().create(pos_order_data)
            print('order created :',order)
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

    def _create_or_get_partner(self, customer_data):
        """Create or get customer partner."""
        print('creating customer')
        Partner = request.env['res.partner'].sudo()
        partner = Partner.search([('email', '=', customer_data['email'])],
                                 limit=1)

        if not partner:
            partner = Partner.create({
                'name': customer_data['name'],
                'email': customer_data['email'],
                'company_name': customer_data['companyName'],
            })

        return partner.id
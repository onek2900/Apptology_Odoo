# -*- coding: utf-8 -*-
import json
import logging

import requests

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class MainServerWebhooks(http.Controller):
    """Controller for handling MainServer webhooks"""

    @http.route('/main_server/deliverect/pos/register', type='http', methods=['POST'], auth="none", csrf=False)
    def register_pos(self):
        print('register pos')
        """
        Webhook for registering POS with Deliverect.
        """
        try:
            data = json.loads(request.httprequest.data)
            pos_id = data.get('externalLocationId')
            main_server_record = request.env['main.server.data'].sudo().search([('pos_id', '=', pos_id)])
            print(main_server_record)
            if main_server_record:
                main_server_record.write({
                    'account_id': data.get('accountId'),
                })
                try:
                    external_response = requests.post(
                        main_server_record.registration_url,
                        json=data,
                        headers={"accept": "application/json"},
                        timeout=30
                    )
                    print(external_response.json())
                    if external_response.json().get('result', {}).get('status') == 'success':
                        main_server_record.write({'customer_pos_status': 'success'})
                        _logger.info("Data successfully sent from the main server to the customer's Odoo instance.")
                    else:
                        main_server_record.write({'customer_pos_status': 'fail'})
                        _logger.warning("Failed to send data from the main server to the customer's Odoo instance.")
                except requests.RequestException as e:
                    _logger.error(f"Failed to call external webhook: {str(e)}")

            response_data = {
                "ordersWebhookURL": main_server_record.order_sync_url,
                "syncProductsURL": main_server_record.product_sync_url,
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

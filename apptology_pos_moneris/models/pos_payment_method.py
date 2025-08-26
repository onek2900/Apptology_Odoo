# coding: utf-8
import logging
import requests
import json
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from odoo import fields, models
from odoo.exceptions import AccessDenied


class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    def _get_payment_terminal_selection(self):
        return super(PosPaymentMethod, self)._get_payment_terminal_selection() + [
            ("moneris", "Moneris")
        ]

    moneris_terminal_id = fields.Char(string='Terminal ID')
    moneris_ist_config_code = fields.Char(string='Moneris IST config code')
    moneris_api_token = fields.Char(string='Moneris API Token')
    moneris_api_version = '3.0'
    moneris_store_id = fields.Char(string='Moneris Store ID')
    moneris_merchant_id = fields.Char(string='Moneris Merchant ID')


    def _is_write_forbidden(self, fields):
        return super(PosPaymentMethod, self)._is_write_forbidden(
            fields - {"moneris_latest_response"}
        )

    def get_latest_moneris_status(self):
        """
        Get the latest Moneris response for the POS Payment Method. Called from the POS front-end.
        """
        self.ensure_one()
        latest_response = self.sudo().moneris_latest_response
        latest_response = json.loads(latest_response) if latest_response else False
        return latest_response


    def send_moneris_payment(self, data):
        config_param = self.env['ir.config_parameter'].sudo()
        

        # Build idempotency key as YYYYMMDD-orderId
        today_str = datetime.now().strftime("%Y%m%d")
        order_id = str(data.get("orderId")).replace(" ", "")  # ensure no spaces
        idempotency_key = f"{today_str}{order_id}"
        
        payload = {
            "apiVersion": "3.0",
            "apiToken": self.moneris_api_token,
            "storeId": self.moneris_store_id,
            "istConfigCode": self.moneris_ist_config_code,
            "dataId": data.get('orderId'),
            "dataTimestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "data": {
                "request": [
                    {
                        "orderId": data.get('orderId'),
                        "idempotencyKey": idempotency_key,
                        "terminalId": self.moneris_terminal_id,
                        "action": "purchase",
                        "totalAmount": str(int(
                                                (Decimal(str(data.get("orderAmount")))
                                                .quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)) * 100
                                            )),
                    }
                ]
            }
        }
        
        endpoint_url = "https://ippostest.moneris.com/v3/terminal"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        _logger = logging.getLogger(__name__)
        _logger.info("Sending Moneris payload: %s", json.dumps(payload, indent=2))

        try:
            _logger.info("Moneris request -> %s", json.dumps(payload, indent=2))
            resp = requests.post(endpoint_url, json=payload, headers=headers, timeout=30)
            _logger.info("Moneris response [%s]: %s", resp.status_code, resp.text)
            resp.raise_for_status()
            return resp.json()
        
        except requests.exceptions.RequestException as e:
            _logger.error("Moneris request failed: %s", str(e))
            return {"error": "request_failed", "message": str(e)}


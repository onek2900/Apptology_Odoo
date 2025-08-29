# coding: utf-8
import logging
import requests
import json
import time
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from odoo import fields, models, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    def _get_payment_terminal_selection(self):
        return super(PosPaymentMethod, self)._get_payment_terminal_selection() + [
            ("moneris", "Moneris")
        ]

    moneris_terminal_id = fields.Char(string='Terminal ID')
    moneris_ist_config_code = fields.Char(string='Moneris IST config code')
    moneris_api_token = fields.Char(string='Moneris API Token')
    moneris_api_version = fields.Char(string='API Version', default='3.0')
    moneris_store_id = fields.Char(string='Moneris Store ID')
    moneris_merchant_id = fields.Char(string='Moneris Merchant ID')
    moneris_latest_response = fields.Text(
        string="Moneris Latest Response",
        help="Stores the last response received from Moneris for polling."
    )
    moneris_last_sync = fields.Datetime(string='Last Sync Time',
                                        help="Last time terminal was synchronized with Moneris")

    @api.model
    def _is_write_forbidden(self, fields):
        return super(PosPaymentMethod, self)._is_write_forbidden(
            fields - {"moneris_latest_response", "moneris_last_sync"}
        )

    def get_latest_moneris_status(self):
        """
        Get the latest Moneris response for the POS Payment Method. Called from the POS front-end.
        """
        self.ensure_one()
        try:
            latest_response = self.sudo().moneris_latest_response
            return json.loads(latest_response) if latest_response else {}
        except json.JSONDecodeError:
            _logger.error("Failed to parse Moneris latest response as JSON")
            return {}

    def send_moneris_payment(self, data):
        """
        Send payment request to Moneris and store response for polling
        """
        self.ensure_one()

        # Check if terminal needs sync (sync if never synced or last sync was more than 1 hour ago)
        if not self.moneris_last_sync or (
                datetime.now() - fields.Datetime.from_string(self.moneris_last_sync)).total_seconds() > 3600:
            sync_result = self.sync_moneris_terminal()
            if sync_result and sync_result.get('error'):
                _logger.warning("Terminal sync failed, but proceeding with payment: %s", sync_result.get('message'))

        if not all([self.moneris_api_token, self.moneris_store_id, self.moneris_ist_config_code,
                    self.moneris_terminal_id]):
            return {"error": "configuration_error", "message": "Moneris payment method is not properly configured"}

        # Build idempotency key as YYYYMMDD-orderId
        today_str = datetime.now().strftime("%Y%m%d")
        order_id = str(data.get("orderId", "")).replace(" ", "")  # ensure no spaces
        idempotency_key = f"{today_str}{order_id}"

        # Convert amount to cents (Moneris expects amount in cents)
        try:
            amount = Decimal(str(data.get("orderAmount", 0)))
            amount_cents = str(int(amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) * 100))
        except:
            amount_cents = "0"

        payload = {
            "apiVersion": self.moneris_api_version,
            "apiToken": self.moneris_api_token,
            "storeId": self.moneris_store_id,
            "istConfigCode": self.moneris_ist_config_code,
            "dataId": data.get('orderId', ''),
            "dataTimestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "data": {
                "request": [
                    {
                        "orderId": data.get('orderId', ''),
                        "idempotencyKey": idempotency_key,
                        "terminalId": self.moneris_terminal_id,
                        "action": "purchase",
                        "totalAmount": amount_cents,
                    }
                ]
            }
        }

        # Use test endpoint for development, production endpoint for live
        endpoint_url = "https://ippostest.moneris.com/v3/terminal"
        if self.env['ir.config_parameter'].sudo().get_param('moneris.production', False):
            endpoint_url = "https://ipgos.moneris.com/v3/terminal"

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        _logger.info("Sending Moneris payment request for order: %s", data.get('orderId', ''))

        try:
            _logger.debug("Moneris request payload: %s", json.dumps(payload, indent=2))
            resp = requests.post(endpoint_url, json=payload, headers=headers, timeout=30)
            _logger.info("Moneris response status: %s", resp.status_code)

            if resp.status_code != 200:
                _logger.error("Moneris API error: %s - %s", resp.status_code, resp.text)
                return {"error": "api_error", "message": f"API returned status {resp.status_code}"}

            response_data = resp.json()
            _logger.debug("Moneris response: %s", json.dumps(response_data, indent=2))

            # Store the response for polling
            self.sudo().write({'moneris_latest_response': json.dumps(response_data)})

            return response_data

        except requests.exceptions.Timeout:
            _logger.error("Moneris request timeout")
            return {"error": "timeout", "message": "Request to payment gateway timed out"}

        except requests.exceptions.ConnectionError:
            _logger.error("Moneris connection error")
            return {"error": "connection_error", "message": "Could not connect to payment gateway"}

        except requests.exceptions.RequestException as e:
            _logger.error("Moneris request failed: %s", str(e))
            return {"error": "request_failed", "message": str(e)}

        except Exception as e:
            _logger.error("Unexpected error in Moneris payment: %s", str(e))
            return {"error": "unexpected_error", "message": "An unexpected error occurred"}

    def sync_moneris_terminal(self):
        """
        Synchronize terminal settings with Moneris
        """
        self.ensure_one()

        if not all([self.moneris_api_token, self.moneris_store_id, self.moneris_ist_config_code,
                    self.moneris_terminal_id, self.moneris_merchant_id]):
            return {"error": "configuration_error", "message": "Moneris payment method is not properly configured"}

        # Generate unique dataId and idempotencyKey
        import uuid
        data_id = str(uuid.uuid4())[:8]
        idempotency_key = str(uuid.uuid4())

        payload = {
            "apiVersion": self.moneris_api_version,
            "apiToken": self.moneris_api_token,
            "storeId": self.moneris_store_id,
            "istConfigCode": self.moneris_ist_config_code,
            "dataId": data_id,
            "dataTimestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "data": {
                "request": [
                    {
                        "idempotencyKey": idempotency_key,
                        "merchantId": self.moneris_merchant_id,
                        "terminalId": self.moneris_terminal_id,
                        "action": "sync"
                    }
                ]
            }
        }

        # Use test endpoint for development, production endpoint for live
        endpoint_url = "https://ippostest.moneris.com/v3/terminal"
        if self.env['ir.config_parameter'].sudo().get_param('moneris.production', False):
            endpoint_url = "https://ipgos.moneris.com/v3/terminal"

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        _logger.info("Sending Moneris sync request")

        try:
            _logger.debug("Moneris sync request: %s", json.dumps(payload, indent=2))
            resp = requests.post(endpoint_url, json=payload, headers=headers, timeout=30)
            _logger.info("Moneris sync response status: %s", resp.status_code)

            if resp.status_code != 200:
                _logger.error("Moneris sync API error: %s - %s", resp.status_code, resp.text)
                return {"error": "api_error", "message": f"Sync API returned status {resp.status_code}"}

            response_data = resp.json()
            _logger.debug("Moneris sync response: %s", json.dumps(response_data, indent=2))

            # Store the receipt URL for sync status checking
            receipt_url = response_data.get('receipt', {}).get('data', {}).get('response', [{}])[0].get('receiptUrl')
            if receipt_url:
                self.sudo().write({'moneris_latest_response': json.dumps(response_data)})
                # Poll the sync status
                return self._poll_sync_status(receipt_url)

            return response_data

        except requests.exceptions.Timeout:
            _logger.error("Moneris sync request timeout")
            return {"error": "timeout", "message": "Sync request timed out"}

        except requests.exceptions.RequestException as e:
            _logger.error("Moneris sync request failed: %s", str(e))
            return {"error": "request_failed", "message": str(e)}

    def _poll_sync_status(self, receipt_url, max_attempts=30, interval=2):
        """
        Poll the sync status until completion
        """
        attempts = 0
        while attempts < max_attempts:
            attempts += 1
            time.sleep(interval)

            response = self.check_moneris_receipt_status(receipt_url)
            if response and not response.get('error'):
                receipt_data = response.get('receipt', {})
                completed = receipt_data.get('Completed') == "true"
                status_code = receipt_data.get('statusCode')

                if completed and status_code == "5206":
                    _logger.info("Moneris terminal sync completed successfully")
                    # Update last sync time
                    self.sudo().write({'moneris_last_sync': datetime.now()})
                    return {"success": True, "message": "Terminal sync completed"}
                elif status_code in ["5206", "5209"] and completed:
                    _logger.info("Moneris terminal sync completed")
                    # Update last sync time
                    self.sudo().write({'moneris_last_sync': datetime.now()})
                    return {"success": True, "message": "Terminal sync completed"}

        _logger.error("Moneris terminal sync timeout")
        return {"error": "timeout", "message": "Terminal sync timed out"}

    def check_moneris_receipt_status(self, receipt_url):
        """
        Check the status from Moneris receipt URL
        """
        self.ensure_one()

        if not receipt_url:
            return {"error": "missing_receipt_url", "message": "No receipt URL provided"}

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        _logger.info("Checking Moneris receipt URL: %s", receipt_url)

        try:
            resp = requests.get(receipt_url, headers=headers, timeout=15)
            _logger.info("Moneris receipt response status: %s", resp.status_code)

            if resp.status_code != 200:
                _logger.error("Moneris receipt API error: %s - %s", resp.status_code, resp.text)
                return {"error": "api_error", "message": f"Receipt API returned status {resp.status_code}"}

            response_data = resp.json()
            _logger.debug("Moneris receipt response: %s", json.dumps(response_data, indent=2))

            # Store the latest response for reference
            self.sudo().write({'moneris_latest_response': json.dumps(response_data)})

            return response_data

        except requests.exceptions.Timeout:
            _logger.error("Moneris receipt request timeout")
            return {"error": "timeout", "message": "Receipt request timed out"}

        except requests.exceptions.ConnectionError:
            _logger.error("Moneris receipt connection error")
            return {"error": "connection_error", "message": "Could not connect to receipt URL"}

        except requests.exceptions.RequestException as e:
            _logger.error("Moneris receipt request failed: %s", str(e))
            return {"error": "request_failed", "message": str(e)}

        except Exception as e:
            _logger.error("Unexpected error in Moneris receipt check: %s", str(e))
            return {"error": "unexpected_error", "message": "An unexpected error occurred"}

    def clear_moneris_response(self):
        """Clear the stored Moneris response"""
        self.ensure_one()
        self.sudo().write({'moneris_latest_response': False})

    def manual_sync_terminal(self):
        """
        Manual terminal synchronization - can be called from UI
        """
        self.ensure_one()
        result = self.sync_moneris_terminal()
        if result and result.get('success'):
            return {"success": True, "message": "Terminal synchronized successfully"}
        else:
            return result or {"error": "sync_failed", "message": "Terminal synchronization failed"}
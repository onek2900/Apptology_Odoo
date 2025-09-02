# coding: utf-8
import logging
import requests
import json
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from odoo import api, fields, models
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

    # Snapshot and raw payload fields for latest Moneris responses
    moneris_latest_response = fields.Text(string='Moneris Latest Response')
    moneris_last_action = fields.Char(string='Moneris Last Action')
    moneris_last_status = fields.Char(string='Moneris Last Status')
    moneris_last_status_code = fields.Char(string='Moneris Last Status Code')
    moneris_last_response_code = fields.Char(string='Moneris Last Response Code')
    moneris_last_completed = fields.Boolean(string='Moneris Last Completed')
    moneris_last_updated = fields.Datetime(string='Moneris Last Updated')

    def _is_write_forbidden(self, fields):
        """Allow updating non-critical Moneris snapshot fields even with open sessions.
        This bypass ensures postback snapshots don't trigger POS write locks.
        """
        allowed = {
            "moneris_latest_response",
            "moneris_last_action",
            "moneris_last_status",
            "moneris_last_status_code",
            "moneris_last_response_code",
            "moneris_last_completed",
            "moneris_last_updated",
        }
        return super(PosPaymentMethod, self)._is_write_forbidden(fields - allowed)

    def get_latest_moneris_status(self):
        """
        Get the latest Moneris response for the POS Payment Method. Called from the POS front-end.
        """
        self.ensure_one()
        latest_response = self.sudo().moneris_latest_response
        latest_response = json.loads(latest_response) if latest_response else False
        return latest_response

    # -------------------------------------------------------------------------
    # PURCHASE
    # -------------------------------------------------------------------------
    def send_moneris_payment(self, data):
        config_param = self.env['ir.config_parameter'].sudo()
        base_url = config_param.get_param('web.base.url') or ''
        postback = f"{base_url}/moneris/postback" if base_url else "https://YOUR_DOMAIN/moneris/postback"

        # Build idempotency key as YYYYMMDDHHMMSS + orderId (no spaces)
        time_str = datetime.now().strftime("%Y%m%d%H%M%S")
        order_id_clean = str(data.get("orderId")).replace(" ", "")  # ensure no spaces
        idempotency_key = f"{time_str}{order_id_clean}"

        payload = {
            "apiVersion": "3.0",
            "apiToken": self.moneris_api_token,
            "storeId": self.moneris_store_id,
            "istConfigCode": self.moneris_ist_config_code,
            "postBackUrl": postback,  # include postback for async callback
            # "polling": "true",      # optional if you also want to poll
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
        _logger.info("Moneris PURCHASE request -> %s", json.dumps(payload, indent=2))

        try:
            resp = requests.post(endpoint_url, json=payload, headers=headers, timeout=30)
            _logger.info("Moneris PURCHASE response [%s]: %s", resp.status_code, resp.text)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            _logger.error("Moneris PURCHASE request failed: %s", str(e))
            return {"error": "request_failed", "message": str(e)}

    # -------------------------------------------------------------------------
    # SYNC
    # -------------------------------------------------------------------------
    def _moneris_sync_terminal(self, session=None):
        """Send SYNC action to Moneris for this payment method's terminal.
        Requires:
          - moneris_api_token, moneris_store_id, moneris_ist_config_code, moneris_terminal_id
        Optionally uses:
          - moneris_merchant_id
        """
        for pm in self:
            api_token = getattr(pm, 'moneris_api_token', False)
            store_id = getattr(pm, 'moneris_store_id', False)
            ist_code = getattr(pm, 'moneris_ist_config_code', False)
            merchant_id = getattr(pm, 'moneris_merchant_id', False)
            terminal_id = getattr(pm, 'moneris_terminal_id', False)

            if not (api_token and store_id and ist_code and terminal_id):
                _logger = logging.getLogger(__name__)
                _logger.warning("Skipping Moneris SYNC: missing credentials on payment method '%s'", pm.display_name)
                # Return a structured error so the frontend can notify the user
                return {
                    "error": "missing_credentials",
                    "message": f"Missing Moneris credentials on payment method '{pm.display_name}'",
                }

            # Build postBackUrl for async callback
            base_url = pm.env['ir.config_parameter'].sudo().get_param('web.base.url') or ''
            postback = f"{base_url}/moneris/postback" if base_url else "https://YOUR_DOMAIN/moneris/postback"

            # Keys/timestamps
            time_str = datetime.now().strftime("%Y%m%d%H%M%S")
            idem_seed = f"POS{session.id}" if session else (str(pm.id) if pm.id else "SYNC")
            idem = f"{time_str}{idem_seed}"  # idempotencyKey includes seconds
            ts_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # proper timestamp format

            request_item = {
                "idempotencyKey": idem,
                "terminalId": terminal_id,
                "action": "sync",
            }
            if merchant_id:
                request_item["merchantId"] = merchant_id  # optional, include if you have it

            payload = {
                "apiVersion": "3.0",
                "apiToken": api_token,
                "storeId": store_id,
                "istConfigCode": ist_code,
                "postBackUrl": postback,  # include postback for async callback
                # "polling": "true",      # optional if you also want to poll
                "dataId": idem,
                "dataTimestamp": ts_str,  # correct format
                "data": {
                    "request": [request_item]
                }
            }

            # Endpoint: default to test; allow optional custom field if you add it later
            endpoint_url = getattr(pm, 'moneris_endpoint_url', False) or "https://ippostest.moneris.com/v3/terminal"
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }

            _logger = logging.getLogger(__name__)
            _logger.info("Moneris SYNC request for terminal %s -> %s", terminal_id, endpoint_url)
            _logger.info("Moneris SYNC payload: %s", json.dumps(payload))

            resp = requests.post(endpoint_url, json=payload, headers=headers, timeout=30)
            _logger.info("Moneris SYNC response [%s]: %s", resp.status_code, resp.text)
            resp.raise_for_status()
            try:
                return resp.json()  # validation response
            except Exception:
                return {"status": "ok"}

    def action_moneris_sync_now(self, session_id=False):
        """RPC: Trigger SYNC on selected Moneris payment methods.
        Returns immediate responses; completion also arrives via postback/bus.
        """
        session = None
        if session_id:
            session = self.env['pos.session'].sudo().browse(int(session_id))
        res = []
        for pm in self:
            try:
                res.append({"id": pm.id, "resp": pm._moneris_sync_terminal(session=session)})
            except Exception as e:
                res.append({"id": pm.id, "error": str(e)})
        return {"results": res}

    @api.model
    def action_moneris_sync_now_for_config(self, config_id, session_id=False):
        """RPC: Trigger SYNC for all Moneris methods on a POS config."""
        _logger = logging.getLogger(__name__)
        _logger.info("Moneris: action_moneris_sync_now_for_config called (config_id=%s, session_id=%s)", config_id, session_id)
        cfg = self.env['pos.config'].sudo().browse(int(config_id))
        if not cfg:
            _logger.warning("Moneris: POS config not found for id=%s", config_id)
            return {"error": "config_not_found"}
        pms = cfg.payment_method_ids.filtered(lambda pm: pm.use_payment_terminal == 'moneris')
        if not pms:
            _logger.warning("Moneris: No Moneris payment methods on config id=%s", config_id)
        return pms.action_moneris_sync_now(session_id=session_id)

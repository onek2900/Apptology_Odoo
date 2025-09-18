# apptology_pos_moneris/controllers/moneris_postback.py
# -*- coding: utf-8 -*-
import logging
import json
from odoo import http, fields
from odoo.http import request

_logger = logging.getLogger(__name__)

class MonerisPostbackController(http.Controller):

    @http.route('/moneris/postback', type='http', auth='public', methods=['GET', 'HEAD'], csrf=False)
    def moneris_postback_probe(self, **kw):
        """Endpoint health probe used by Moneris before sending the real POST callback."""
        return request.make_json_response({"ok": True})

    @http.route('/moneris/postback', type='http', auth='public', methods=['POST'], csrf=False)
    def moneris_postback(self, **kw):
        """
        Moneris posts PLAIN JSON (not JSON-RPC). We use type='http' and read the raw body.

        Flow:
          1) Log headers + raw body + parsed JSON (BEFORE processing)
          2) Process:
             - action == "sync": push sync_success / sync_failed
             - otherwise (e.g., purchase): push purchase with approved flag
          3) Update matching pos.payment.method records (by terminalId) with latest snapshot
          4) ACK with 200 JSON

        NOTE: Odoo 17 bus API => _sendone(channel, message)
        """
        # --- 1) Log headers & body (BEFORE processing) ---
        try:
            hdrs = dict(request.httprequest.headers or {})
            _logger.info("Moneris postBackUrl headers: %s", hdrs)
        except Exception as e:
            _logger.info("Moneris postBackUrl headers: <error reading headers: %s>", e)

        raw = request.httprequest.get_data(as_text=True)  # exact bytes -> str
        _logger.info("=== Moneris postBackUrl RAW body START ===\n%s\n=== Moneris postBackUrl RAW body END ===", raw)

        payload = {}
        try:
            if raw:
                payload = json.loads(raw)
                _logger.info(
                    "=== Moneris postBackUrl parsed JSON START ===\n%s\n=== Moneris postBackUrl parsed JSON END ===",
                    json.dumps(payload, indent=2, ensure_ascii=False),
                )
            else:
                _logger.info("Moneris postBackUrl: empty body")
        except Exception as e:
            _logger.warning("Moneris postBackUrl body is not valid JSON: %s", e)
            # keep payload = {}

        # --- 2) Processing & bus push ---
        try:
            receipt = payload.get("receipt", {}) or {}
            data = receipt.get("data", {}) or {}
            responses = data.get("response", []) or []
            if not responses:
                return request.make_json_response({"ok": True})  # nothing to do

            # Process the first response (extend to loop if needed)
            r = responses[0]
            action         = r.get("action")
            terminal_id    = r.get("terminalId")
            # Some Moneris responses omit orderId in response item; fallback to receipt.dataId
            order_id       = r.get("orderId") or receipt.get("dataId")
            status         = r.get("status")
            status_code    = str(r.get("statusCode", "") or "")
            response_code  = str(r.get("responseCode", "") or "")
            completed      = str(r.get("completed", "false")).lower() == "true"
            error_details  = r.get("errorDetails") or []

            # Determine message type & flags
            if action == "sync":
                # Treat sync success as completed + known OK codes or OK-ish status text
                ok_codes = {"5207", "5209"}
                status_text = (status or "").strip().lower()
                code_ok = status_code in ok_codes
                text_ok = status_text in {"approved", "success", "completed", "ok"}
                sync_ok = completed and (code_ok or text_ok)
                bus_msg = {
                    "type": "sync_success" if sync_ok else "sync_failed",
                    "completed": completed,
                    "status": status,
                    "statusCode": status_code,
                    "terminalId": terminal_id,
                    "errorDetails": error_details,
                }
            elif action == "purchase":
                # Purchase: consider Moneris status text/code, not only responseCode
                status_text = (status or "").strip().lower()
                approved_codes = {"000", "027"}  # common approved response codes
                ok_status_codes = {"5207", "5209"}  # Moneris Approved / Completed
                approved = (
                    completed and (
                        status_text in {"approved", "success", "completed"}
                        or status_code in ok_status_codes
                        or response_code in approved_codes
                    )
                )
                bus_msg = {
                    "type": "purchase",
                    "approved": approved,
                    "completed": completed,
                    "status": status,
                    "statusCode": status_code,
                    "responseCode": response_code,
                    "orderId": order_id,
                    "terminalId": terminal_id,
                    "approvedAmount": r.get("approvedAmount"),
                    "tenderType": r.get("tenderType"),
                    "cardType": r.get("cardType"),
                    "transactionId": r.get("transactionId"),
                    "authCode": r.get("authCode"),
                    "errorDetails": error_details,
                }
            else:
                # Fallback minimal message
                bus_msg = {
                    "type": ("terminal_error" if (status and "error" in str(status).lower()) or error_details else (action or "unknown")),
                    "completed": completed,
                    "status": status,
                    "statusCode": status_code,
                    "orderId": order_id,
                    "terminalId": terminal_id,
                    "errorDetails": error_details,
                }

            # Find target POS configs by terminal mapping (fallback: all configs)
            cfg_ids = set()
            if terminal_id:
                pms = request.env["pos.payment.method"].sudo().search([("moneris_terminal_id", "=", terminal_id)])
                for pm in pms:
                    for cfg in pm.config_ids:
                        cfg_ids.add(cfg.id)
            if not cfg_ids:
                cfg_ids = set(request.env["pos.config"].sudo().search([]).ids)

            # Push to per-config channels (Odoo 17: _sendone(channel, message))
            for cfg_id in cfg_ids:
                channel = f"pos_moneris_{cfg_id}"
                # Build a wrapped payload including channel for client-side filtering
                wrapped = {"channel": channel, "message": bus_msg}
                bus = request.env["bus.bus"].sudo()
                # Compatibility: Some versions expect _sendone(channel, type, message),
                # others expect _sendone(channel, message)
                try:
                    bus._sendone(channel, "notification", wrapped)
                except TypeError:
                    bus._sendone(channel, wrapped)

            # --- 3) Persist snapshot on pos.payment.method (declined/cancelled/approved alike) ---
            snapshot_vals = {
                "moneris_last_action": action,
                "moneris_last_status": status,
                "moneris_last_status_code": status_code,
                "moneris_last_response_code": response_code,
                "moneris_last_completed": completed,
                "moneris_last_updated": fields.Datetime.now(),
                "moneris_latest_response": json.dumps(payload, ensure_ascii=False),
            }
            # Only write keys that exist on the model (safe if some fields aren't defined)
            pm_model = request.env["pos.payment.method"].sudo()
            existing_fields = pm_model.fields_get(snapshot_vals.keys())
            safe_vals = {k: v for k, v in snapshot_vals.items() if k in existing_fields}

            if safe_vals:
                if terminal_id:
                    pms = pm_model.search([("moneris_terminal_id", "=", terminal_id)])
                else:
                    pms = pm_model.search([])
                if pms:
                    pms.write(safe_vals)

        except Exception as e:
            _logger.exception("Moneris postback processing failed: %s", e)

        # --- 4) Minimal ACK so Moneris doesn’t retry ---
        return request.make_json_response({"ok": True})

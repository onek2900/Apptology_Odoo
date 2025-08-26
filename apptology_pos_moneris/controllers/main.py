import json
import pprint

from odoo import http, _, fields, Command
import logging

from odoo.http import request, Response

_logger = logging.getLogger(__name__)


class PosMonerisController(http.Controller):

    @http.route(
        "/apptology_pos_moneris/notification",
        type="http",
        auth="public",
        csrf=False,
        methods=["POST"],
    )
    def moneris_return(self, **kwargs):
        """Handles Moneris POST notifications."""
        try:
            json_data = json.loads(request.httprequest.data)
        except json.JSONDecodeError:
            _logger.error("Invalid JSON data received.")
            return {"error": "Invalid JSON data"}, 400

        _logger.info("Moneris Parsed JSON data: %s", pprint.pformat(json_data))
        payment_complete = True
        if payment_complete:
            return self._handle_transaction(json_data)

        else:
            _logger.error("Invalid data received %s", json_data)
            return {"error": "Invalid event type"}, 400

    def _handle_transaction(self, json_data):
        try:

            # Verify HMAC
            # terminal_id = json_data["obj"]["terminal_id"]
            record = request.env["pos.payment.method"].sudo().search([("moneris_terminal_id", "=", "abc")],
                                                                     limit=1)

            # extract information and validate
            pos_session_id=4

            paymob_pm_sudo = (
                request.env["pos.payment.method"]
                .sudo()
                .search([("moneris_terminal_id", "=", "abc")], limit=1)
            )
            if not paymob_pm_sudo:
                _logger.error("Terminal ID not found in odoo system")
                return {"error": "Terminal ID not found"}, 400
            pos_session_sudo = (
                request.env["pos.session"].sudo().browse(int(pos_session_id))
            )
            if not pos_session_sudo:
                _logger.error("POS session not found in odoo system")
                return {"error": "POS session not found"}, 400

            # update the transaction, notify the POS session
            paymob_pm_sudo.moneris_latest_response = json.dumps(json_data)
            request.env['bus.bus'].sudo()._sendone(pos_session_sudo._get_bus_channel_name(), 'MONERIS_LATEST_RESPONSE',
                                                   {"session_id":pos_session_sudo.id})

        except Exception as e:
            _logger.error("Error handling transaction: %s", e)

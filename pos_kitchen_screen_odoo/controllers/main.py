# -*- coding: utf-8 -*-

import logging
import werkzeug

from odoo import http, fields
from odoo.http import request

_logger = logging.getLogger(__name__)


class OrderScreen(http.Controller):

    @http.route("/pos/kitchen/get_order_details", auth="public", type="json", website=False)
    def get_pos_kitchen_order_details(self, shop_id):
        kitchen_screen = request.env["kitchen.screen"].sudo().search(
            [("pos_config_id", "=", shop_id)], limit=1)

        # Resolve the exact current session from POS config to avoid picking a stale opened session
        config = request.env["pos.config"].sudo().browse(int(shop_id))
        pos_session_id = config.current_session_id
        if not pos_session_id:
            return {"orders": [], "order_lines": [], "error": "no_open_session"}

        # Build domains with optional category filter; if no categories chosen, show all
        cat_domain = []
        if kitchen_screen.pos_categ_ids:
            cat_domain = [("lines.product_id.pos_categ_ids", "in", kitchen_screen.pos_categ_ids.ids)]

        # In‑progress: only orders with cooking lines; split in‑store vs online (allow open/approved/finalized)
        pos_orders = request.env["pos.order"].sudo().search(
            [("lines.is_cooking", "=", True), ("is_online_order", "=", False), ("session_id", "=", pos_session_id.id)]
            + cat_domain,
            order="date_order",
        )

        approved_deliverect_orders = request.env["pos.order"].sudo().search(
            [
                ("lines.is_cooking", "=", True),
                ("session_id", "=", pos_session_id.id),
                ("is_online_order", "=", True),
                # Only show approved/finalized online orders in kitchen (exclude 'open')
                ("online_order_status", "in", ["approved", "finalized"]),
            ]
            + cat_domain,
            order="date_order",
        )

        # Completed: include READY orders for the same session (ignore is_cooking flags)
        ready_instore = request.env["pos.order"].sudo().search(
            [("order_status", "=", "ready"), ("is_online_order", "=", False), ("session_id", "=", pos_session_id.id)]
            + cat_domain,
            order="date_order",
        )
        ready_online = request.env["pos.order"].sudo().search(
            [
                ("order_status", "=", "ready"),
                ("session_id", "=", pos_session_id.id),
                ("is_online_order", "=", True),
                ("online_order_status", "in", ["approved", "finalized"]),
            ]
            + cat_domain,
            order="date_order",
        )

        combined_orders = pos_orders | approved_deliverect_orders | ready_instore | ready_online

        # Debug/diagnostic logging
        try:
            _logger.info(
                "[KitchenAPI] shop=%s session=%s cats=%s counts in_progress(instore=%s, online=%s) ready(instore=%s, online=%s)",
                shop_id,
                pos_session_id.id,
                kitchen_screen.pos_categ_ids.ids if kitchen_screen else [],
                len(pos_orders),
                len(approved_deliverect_orders),
                len(ready_instore),
                len(ready_online),
            )
            _logger.debug(
                "[KitchenAPI] ids in_progress(instore=%s, online=%s) ready(instore=%s, online=%s)",
                pos_orders.ids,
                approved_deliverect_orders.ids,
                ready_instore.ids,
                ready_online.ids,
            )
        except Exception:
            pass
        values = {"orders": combined_orders.read(), "order_lines": combined_orders.lines.read()}
        return values

    @http.route("/apptology_kitchen_screen", auth="public", type="http", website=True)
    def apptology_kitchen_screen(self, shop_id):
        query = f"""SELECT id from pos_config where id = {int(shop_id)} limit 1"""
        request.env.cr.execute(query)
        shop = request.env.cr.dictfetchone()
        if shop is None:
            raise werkzeug.exceptions.NotFound()

        context = {
            "session_info": {
                **request.env["ir.http"].get_frontend_session_info(),
                'shop_id': shop.get('id'),
                # Boot token to force client-side refresh/reset on page open
                'kitchen_boot_ts': fields.Datetime.now().isoformat(),
            },
            "shop_id": shop.get('id'),
            "title": "Pos Kitchen Screen",
            "screen": "kitchen",
        }
        return request.render("pos_kitchen_screen_odoo.index", context)

    @http.route("/pos/kitchen/order_status", auth="public", type="json", website=False)
    def change_order_status(self, method, order_id):
        order_sudo = request.env["pos.order"].sudo().browse(order_id)
        if hasattr(order_sudo, method):
            method_to_call = getattr(order_sudo, method)
            result = method_to_call()
            return result
        return False

    @http.route("/pos/kitchen/line_status", auth="public", type="json", website=False)
    def change_order_line_status(self, line_ids=None):
        """Toggle the readiness of given order line(s) using sudo.

        Accepts a single id or a list of ids in `line_ids`.
        Returns True on success, False otherwise.
        """
        if not line_ids:
            return False
        # Normalize and validate ids
        ids = []
        try:
            if isinstance(line_ids, (int, str)):
                ids = [int(line_ids)]
            elif isinstance(line_ids, (list, tuple)):
                ids = [int(x) for x in line_ids]
        except Exception:
            return False
        ids = [i for i in ids if isinstance(i, int) and i > 0]
        if not ids:
            return False
        # Filter to existing records to avoid warnings on invalid ids
        lines = request.env["pos.order.line"].sudo().browse(ids).exists()
        if not lines:
            return False
        lines.order_progress_change()
        return True

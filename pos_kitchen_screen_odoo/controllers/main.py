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
        # Include per-press kitchen tickets for these orders
        tickets = request.env["pos.kitchen.ticket"].sudo().search([("order_id", "in", combined_orders.ids)])
        # Filter out empty tickets (no lines) for cleaner UI payload
        tickets = tickets.filtered(lambda t: bool(t.line_ids))
        values = {
            "orders": combined_orders.read(),
            "order_lines": combined_orders.lines.read(),
            "tickets": tickets.read(["id", "order_id", "line_ids", "press_index", "ticket_uid", "created_at", "state"]),
        }
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

    @http.route("/pos/kitchen/get_ticket_lines", auth="public", type="json", website=False)
    def get_ticket_lines(self, shop_id=None, order_ref=None, ticket_uid=None):
        """Return real pos.order.line ids for a given ticket_uid.

        Optionally restrict by current opened session of shop_id.
        """
        if not ticket_uid:
            return {"line_ids": [], "order_id": False}
        domain = [("kitchen_ticket_uid", "=", str(ticket_uid))]
        if shop_id:
            config = request.env["pos.config"].sudo().browse(int(shop_id))
            session = config.current_session_id
            if session:
                domain = request.env["pos.order.line"].sudo()._where_calc(domain).get_sql()
        lines = request.env["pos.order.line"].sudo().search([("kitchen_ticket_uid", "=", str(ticket_uid))])
        order_id = lines[:1].order_id.id if lines else False
        return {"line_ids": lines.ids, "order_id": order_id}

    @http.route("/pos/kitchen/resolve_ticket", auth="public", type="json", website=False)
    def resolve_ticket(self, shop_id=None, ticket_uid=None):
        """Broadcast a resolution message mapping a ticket_uid to real line_ids."""
        try:
            out = self.get_ticket_lines(shop_id=shop_id, ticket_uid=ticket_uid)
            payload = {
                "type": "kitchen_ticket_resolved",
                "shop_id": int(shop_id) if shop_id else None,
                "ticket_uid": ticket_uid,
                "line_ids": out.get("line_ids", []),
                "order_id": out.get("order_id"),
            }
            # Send bus notification on channel 'kitchen.delta'
            request.env["bus.bus"]._sendone("kitchen.delta", "notification", payload)
            return {"ok": True, **payload}
        except Exception:
            return {"ok": False}

    @http.route("/pos/kitchen/push_delta", auth="public", type="json", website=False)
    def push_delta_to_kitchen(self, shop_id=None, order_ref=None, ticket_uid=None, new_lines=None, meta=None):
        """Receive a delta from POS and broadcast it to kitchen screens via bus.

        This avoids a full refresh: the kitchen UI can render the payload directly.
        Expected payload:
          - shop_id: POS config id
          - order_ref: pos_reference string
          - ticket_uid: client-generated unique id for this press
          - new_lines: list of {product_id, product_name, quantity, note}
          - meta: optional dict with partner, table, floor, order_type, is_online_order
        """
        try:
            shop_id = int(shop_id) if shop_id is not None else None
        except Exception:
            shop_id = None
        if not shop_id:
            return {"ok": False}
        payload = {
            "type": "kitchen_delta",
            "shop_id": shop_id,
            "order_ref": order_ref or "",
            "ticket_uid": ticket_uid or f"ticket_{fields.Datetime.now().timestamp()}",
            "items": new_lines or [],
            "meta": meta or {},
        }
        # Fanout to the custom kitchen channel; clients subscribe via bus_service
        request.env["bus.bus"]._sendone("kitchen.delta", "notification", payload)
        return {"ok": True}

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

        # Build domains safely even if online order fields do not exist
        Order = request.env["pos.order"].sudo()
        has_online = "is_online_order" in Order._fields
        has_online_status = "online_order_status" in Order._fields

        # In-progress: only orders with cooking lines
        pos_orders_domain = [("lines.is_cooking", "=", True), ("session_id", "=", pos_session_id.id)] + cat_domain
        if has_online:
            pos_orders_domain.append(("is_online_order", "=", False))
        pos_orders = Order.search(pos_orders_domain, order="date_order")

        # Online in-progress (only when fields exist)
        if has_online:
            online_dom = [("lines.is_cooking", "=", True), ("session_id", "=", pos_session_id.id)] + cat_domain
            online_dom.append(("is_online_order", "=", True))
            if has_online_status:
                online_dom.append(("online_order_status", "in", ["approved", "finalized"]))
            approved_deliverect_orders = Order.search(online_dom, order="date_order")
        else:
            approved_deliverect_orders = Order.browse([])

        # Completed: include READY orders for the same session (ignore is_cooking flags)
        ready_instore_domain = [("order_status", "=", "ready"), ("session_id", "=", pos_session_id.id)] + cat_domain
        if has_online:
            ready_instore_domain.append(("is_online_order", "=", False))
        ready_instore = Order.search(ready_instore_domain, order="date_order")

        if has_online:
            ready_online_dom = [("order_status", "=", "ready"), ("session_id", "=", pos_session_id.id)] + cat_domain
            ready_online_dom.append(("is_online_order", "=", True))
            if has_online_status:
                ready_online_dom.append(("online_order_status", "in", ["approved", "finalized"]))
            ready_online = Order.search(ready_online_dom, order="date_order")
        else:
            ready_online = Order.browse([])

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
        # Keep a ticket if it has server lines or a saved snapshot
        tickets = tickets.filtered(lambda t: bool(t.line_ids) or bool(getattr(t, 'snapshot', False)))
        values = {
            "orders": combined_orders.read(),
            "order_lines": combined_orders.lines.read(),
            "tickets": tickets.read(["id", "order_id", "line_ids", "press_index", "ticket_uid", "created_at", "state", "snapshot"]),
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
    def change_order_line_status(self, line_ids=None, status=None):
        """Update the readiness of given order line(s).

        Accepts a single id or a list of ids in `line_ids`.
        Optional `status` can be provided to set an explicit target value
        (e.g., `ready`/`waiting`). Falls back to toggle behaviour for
        legacy callers.
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

        lines = request.env["pos.order.line"].sudo().browse(ids).exists()
        if not lines:
            return False

        target = None
        if isinstance(status, str):
            normalized = status.strip().lower()
            alias = {
                "ready": "ready",
                "completed": "ready",
                "done": "ready",
                "waiting": "waiting",
                "cooking": "waiting",
                "draft": "draft",
                "cancel": "cancel",
                "cancelled": "cancel",
            }
            target = alias.get(normalized)

        if target:
            pending_states = {"draft", "waiting"}
            lines.write({
                "order_status": target,
                "is_cooking": target in pending_states,
            })
        else:
            lines.order_progress_change()
            pending_states = {"draft", "waiting"}
            refreshed = request.env["pos.order.line"].sudo().browse(lines.ids)
            ready_lines = refreshed.filtered(lambda l: l.order_status not in pending_states)
            cooking_lines = refreshed - ready_lines
            if ready_lines:
                ready_lines.write({"is_cooking": False})
            if cooking_lines:
                cooking_lines.write({"is_cooking": True})
        orders = lines.mapped("order_id")
        if orders:
            orders.order_progress_change()
        return True

    @http.route("/pos/kitchen/get_ticket_lines", auth="public", type="json", website=False)
    def get_ticket_lines(self, shop_id=None, order_ref=None, ticket_uid=None):
        """Return real pos.order.line ids for a given ticket_uid.

        Additional params are kept for backward compatibility with legacy clients.
        """
        if not ticket_uid:
            return {"line_ids": [], "order_id": False}
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

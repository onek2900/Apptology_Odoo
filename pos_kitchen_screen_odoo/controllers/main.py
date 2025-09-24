# -*- coding: utf-8 -*-

import werkzeug

from odoo import http
from odoo.http import request


class OrderScreen(http.Controller):
    @http.route("/pos.order/get_order_details", auth="public", type="json", website=False)
    def get_pos_order_details(self, screen_id):
        kitchen_screen = request.env["kitchen.screen"].sudo().browse(int(screen_id))

        pos_session_id = request.env["pos.session"].sudo().search([
            ('config_id', '=', kitchen_screen.pos_config_id.id),
            ('state', '=', 'opened')], limit=1)
        # Build domains with optional category filter; if no categories chosen, show all
        cat_domain = []
        if kitchen_screen.pos_categ_ids:
            cat_domain = [("lines.product_id.pos_categ_ids", "in", kitchen_screen.pos_categ_ids.ids)]

        pos_order_model = request.env["pos.order"].sudo()
        has_online_flag = "is_online_order" in pos_order_model._fields
        has_online_status = "online_order_status" in pos_order_model._fields

        # Only consider orders still in progress; exclude those already marked ready
        base_domain = [
            ("lines.is_cooking", "=", True),
            ("order_status", "!=", "ready"),
            ("session_id", "=", pos_session_id.id),
        ] + cat_domain
        in_store_domain = list(base_domain)
        if has_online_flag:
            in_store_domain.append(("is_online_order", "=", False))

        pos_orders = pos_order_model.search(in_store_domain, order="date_order")

        approved_deliverect_orders = pos_order_model.browse()
        if has_online_flag:
            approved_domain = list(base_domain) + [("is_online_order", "=", True)]
            if has_online_status:
                approved_domain.append(("online_order_status", "=", "approved"))
            approved_deliverect_orders = pos_order_model.search(approved_domain, order="date_order")

        combined_orders = pos_orders | approved_deliverect_orders
        values = {"orders": combined_orders.sudo().read()}
        return values

    @http.route("/apptology_order_screen", auth="public", type="http", website=True)
    def apptology_order_screen(self, screen_id):

        query = f"""SELECT id from kitchen_screen where id = {int(screen_id)} limit 1"""
        request.env.cr.execute(query)
        kitchen_screen = request.env.cr.dictfetchone()
        if kitchen_screen is None:
            raise werkzeug.exceptions.NotFound()

        context = {
            "session_info": {
                **request.env["ir.http"].get_frontend_session_info(),
                'kitchen_screen': kitchen_screen.get('id')
            },
            "kitchen_screen": kitchen_screen.get('id'),
            "title": "Pos Order Tracking",
            "screen": "order",
        }
        return request.render("pos_kitchen_screen_odoo.index", context)

    @http.route("/pos/kitchen/get_order_details", auth="public", type="json", website=False)
    def get_pos_kitchen_order_details(self, shop_id):
        kitchen_screen = request.env["kitchen.screen"].sudo().search(
            [("pos_config_id", "=", shop_id)], limit=1)

        # Use the config's current_session_id to avoid picking an older opened session
        config = request.env["pos.config"].sudo().browse(shop_id)
        pos_session_id = config.current_session_id
        if not pos_session_id:
            return {"orders": [], "order_lines": [], "error": "no_open_session"}

        # Build domains with optional category filter; if no categories chosen, show all
        cat_domain = []
        if kitchen_screen.pos_categ_ids:
            cat_domain = [("lines.product_id.pos_categ_ids", "in", kitchen_screen.pos_categ_ids.ids)]

        pos_order_model = request.env["pos.order"].sudo()
        has_online_flag = "is_online_order" in pos_order_model._fields
        has_online_status = "online_order_status" in pos_order_model._fields

        # Ready-only view for kitchen screen:
        # - Only include orders already marked as 'ready'
        # - Ignore any 'is_cooking' flags on lines (requested behavior)
        base_domain = [
            ("order_status", "=", "ready"),
            ("session_id", "=", pos_session_id.id),
        ] + cat_domain
        in_store_domain = list(base_domain)
        if has_online_flag:
            in_store_domain.append(("is_online_order", "=", False))

        pos_orders = pos_order_model.search(in_store_domain, order="date_order")

        approved_deliverect_orders = pos_order_model.browse()
        if has_online_flag:
            approved_domain = list(base_domain) + [("is_online_order", "=", True)]
            if has_online_status:
                approved_domain.append(("online_order_status", "=", "approved"))
            approved_deliverect_orders = pos_order_model.search(approved_domain, order="date_order")

        combined_orders = pos_orders | approved_deliverect_orders
        values = {"orders": combined_orders.read(), "order_lines": combined_orders.lines.read()}
        # print(values,"values")
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
                'shop_id': shop.get('id')
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
        if isinstance(line_ids, (int, str)):
            try:
                line_ids = [int(line_ids)]
            except Exception:
                return False
        lines = request.env["pos.order.line"].sudo().browse(line_ids)
        if not lines:
            return False
        lines.order_progress_change()
        return True

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

        pos_orders = request.env["pos.order"].sudo().search(
            [("lines.is_cooking", "=", True), ("is_online_order", "=", False),
             ('session_id', '=', pos_session_id.id)] + cat_domain, order="date_order")

        approved_deliverect_orders = request.env["pos.order"].sudo().search(
            [("lines.is_cooking", "=", True),
             ("session_id", "=", pos_session_id.id),
             ("is_online_order", "=", True),
             ("online_order_status", "=", 'approved')] + cat_domain,
            order="date_order")
        combined_orders = pos_orders | approved_deliverect_orders
        values = {
            "orders": combined_orders.sudo().read(),
            "max_lines_per_card": int(kitchen_screen.max_lines_per_card or 0),
        }
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

        pos_session_id = request.env["pos.session"].sudo().search(
            [('config_id', '=', shop_id), ('state', '=', 'opened')],
            limit=1)
        # Build domains with optional category filter; if no categories chosen, show all
        cat_domain = []
        if kitchen_screen.pos_categ_ids:
            cat_domain = [("lines.product_id.pos_categ_ids", "in", kitchen_screen.pos_categ_ids.ids)]

        pos_orders = request.env["pos.order"].sudo().search(
            [("lines.is_cooking", "=", True), ("is_online_order", "=", False),
             ('session_id', '=', pos_session_id.id)] + cat_domain,
            order="date_order")

        approved_deliverect_orders = request.env["pos.order"].sudo().search(
            [("lines.is_cooking", "=", True),
             ("session_id", "=", pos_session_id.id),
             ("is_online_order", "=", True),
             ("online_order_status", "=", 'approved')] + cat_domain,
            order="date_order")

        combined_orders = pos_orders | approved_deliverect_orders
        values = {
            "orders": combined_orders.read(),
            "order_lines": combined_orders.lines.read(),
            "max_lines_per_card": int(kitchen_screen.max_lines_per_card or 0),
        }
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

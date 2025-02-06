# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request


class CustomerScreen(http.Controller):

    @http.route("/apptology_customer_screen", auth="public", type="http",
                website=True)
    def apptology_customer_screen(self):
        context = {
            "session_info": {
                **request.env["ir.http"].get_frontend_session_info()},
            "title": "Customer Screen",
            "screen": "customer",
        }
        return request.render("apptology_customer_screen.index", context)

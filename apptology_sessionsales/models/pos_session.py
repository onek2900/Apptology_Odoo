# -*- coding: utf-8 -*-

from odoo import models


class PosSession(models.Model):
    _inherit = "pos.session"

    def action_print_closure_report(self):
        """Return the built-in session summary report action for the current session."""
        self.ensure_one()

        report_action = self.env.ref("point_of_sale.pos_session_report_action", raise_if_not_found=False)
        if not report_action:
            report_action = self.env.ref("point_of_sale.action_report_pos_order", raise_if_not_found=False)
        if not report_action:
            report_action = self.env["ir.actions.report"].search(
                [
                    ("model", "=", "pos.session"),
                    ("report_name", "in", [
                        "point_of_sale.report_sessionsummary",
                        "point_of_sale.report_sessionsales",
                    ]),
                ],
                limit=1,
            )
        if not report_action:
            return False
        return report_action.report_action(self)

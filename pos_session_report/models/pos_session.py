from odoo import models

class PosSession(models.Model):
    _inherit = 'pos.session'

    def action_open_sale_details_report(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sale Details Report',
            'view_mode': 'form',
            'res_model': 'pos.session',  # Correct model
            'target': 'new',
        }

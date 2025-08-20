# Copyright (C) Softhealer Technologies.
# Part of Softhealer Technologies.

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ResConfigInherit(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_sh_dispaly_purchase_btn = fields.Boolean(
        related="pos_config_id.sh_dispaly_purchase_btn", readonly=False)
    pos_select_purchase_state = fields.Selection(
        related="pos_config_id.select_purchase_state", readonly=False)

    @api.onchange('pos_sh_dispaly_purchase_btn')
    def _onchange_sh_display_purchase_btn(self):
        stock_app = self.env['ir.module.module'].sudo().search([('name', '=', 'purchase')], limit=1)
        if self.pos_sh_dispaly_purchase_btn:
            if stock_app.state != 'installed':
                self.pos_sh_dispaly_purchase_btn = False
                raise UserError('Purchase Module not installed ! \n Please install Sale module first.')
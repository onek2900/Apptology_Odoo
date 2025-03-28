# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    """Inherited ResConfigSettings model to add account_id and pos_id fields."""
    _inherit = 'res.config.settings'

    pos_account_id = fields.Char(string="Account ID",related='pos_config_id.account_id',readonly=False)
    pos_pos_id = fields.Char(string="POS ID",related='pos_config_id.pos_id', readonly=False)

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('pos_account_id', self.pos_account_id or '')
        self.env['ir.config_parameter'].sudo().set_param('pos_pos_id', self.pos_pos_id or '')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        config_parameter = self.env['ir.config_parameter'].sudo()
        res.update(
            pos_account_id=config_parameter.get_param('pos_account_id', ''),
            pos_pos_id=config_parameter.get_param('pos_pos_id', ''),
        )
        return res

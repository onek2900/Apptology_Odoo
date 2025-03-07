# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    """Inherited ResConfigSettings model to add client_id and client_secret fields."""
    _inherit = 'res.config.settings'

    client_id = fields.Char(string="Client ID",help="Enter your client ID Provided by Deliverect.")
    client_secret = fields.Char(string="Client Secret",help="Enter your client secret Provided by Deliverect.")

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('client_id', self.client_id or '')
        self.env['ir.config_parameter'].sudo().set_param('client_secret', self.client_secret or '')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        config_parameter = self.env['ir.config_parameter'].sudo()
        res.update(
            client_id=config_parameter.get_param('client_id', ''),
            client_secret=config_parameter.get_param('client_secret', ''),
        )
        return res

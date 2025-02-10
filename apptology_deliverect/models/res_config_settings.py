from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    client_id = fields.Char(string="Client ID")
    client_secret = fields.Char(string="Client Secret")
    account_id = fields.Char(string="Account ID")
    location_id = fields.Char(string="Location ID")

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('client_id', self.client_id or '')
        self.env['ir.config_parameter'].sudo().set_param('client_secret', self.client_secret or '')
        self.env['ir.config_parameter'].sudo().set_param('account_id', self.account_id or '')
        self.env['ir.config_parameter'].sudo().set_param('location_id', self.location_id or '')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        config_parameter = self.env['ir.config_parameter'].sudo()
        res.update(
            client_id=config_parameter.get_param('client_id', ''),
            client_secret=config_parameter.get_param('client_secret', ''),
            account_id=config_parameter.get_param('account_id', ''),
            location_id=config_parameter.get_param('location_id', '')
        )
        return res
# -*- coding: utf-8 -*-
from odoo import models, fields


class MainServerInfoWizard(models.TransientModel):
    """Class for Deliverect Information Wizard"""
    _name = 'main.server.info.wizard'
    _description = 'Main Server Information Wizard'

    registration_url = fields.Char(
        string='Registration Url',
        help='Registration url used for pos registration',
        default=lambda self: self.env['ir.config_parameter'].sudo().get_param('web.base.url') + '/main_server/deliverect/pos/register'
    )

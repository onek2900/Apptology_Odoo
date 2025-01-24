# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    enable_gsheet_import = fields.Boolean(string='Enable Google Sheet Import',
        config_parameter='product_gsheet_import.enable_gsheet_import')
    gsheet_url = fields.Char(string='Google Sheet URL',
        config_parameter='product_gsheet_import.gsheet_url')
    gsheet_credentials = fields.Char(
        string='Google Service Account Credentials',
        config_parameter='product_gsheet_import.gsheet_credentials',
        help='Paste the contents of your Google Service Account JSON credentials file here'
    )

# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    sh_multi_barcode_unique = fields.Boolean('Is Multi Barcode Unique ?')

class ResConfigSetting(models.TransientModel):
    _inherit = 'res.config.settings'

    sh_multi_barcode_unique = fields.Boolean(string="Is Multi Barcode Unique ?",related='company_id.sh_multi_barcode_unique',readonly=False)

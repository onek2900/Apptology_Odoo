# Copyright (C) Softhealer Technologies.
# Part of Softhealer Technologies.

from odoo import models, fields, api

class PosConfig(models.Model):
    _inherit = 'pos.config'

    sh_enable_own_customer = fields.Boolean(string='Enable Own Customer')

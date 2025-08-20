# Copyright (C) Softhealer Technologies.
# Part of Softhealer Technologies.

from odoo import models, fields

class PosConfigInherit(models.Model):
    _inherit = 'pos.config'

    sh_pos_enable_customer_max_discount = fields.Boolean(
        string='Enable Customer Maximum Discount')

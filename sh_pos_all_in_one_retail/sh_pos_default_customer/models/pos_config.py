# Copyright (C) Softhealer Technologies.
# Part of Softhealer Technologies.

from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    sh_enable_default_customer = fields.Boolean("Enable POS Default Customer")
    sh_default_customer_id = fields.Many2one(
        'res.partner', string="Default Customer")

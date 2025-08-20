# Copyright (C) Softhealer Technologies.
# Part of Softhealer Technologies.

from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    sh_display_sale_btn = fields.Boolean(string="Enable sale order")
    select_order_state = fields.Selection([('quotation', 'Quotation'), ('confirm', 'Sale Order')], string="Select Order State ", default="quotation")

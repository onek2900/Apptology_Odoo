# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.


from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    sh_apply_custom_discount = fields.Boolean(
        string="Apply Custom Discount Using Standard Discount Button ")
    sh_apply_both_discount = fields.Boolean(string="Apply Custom Discount")


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    sh_discount_code = fields.Char('Discount Code')

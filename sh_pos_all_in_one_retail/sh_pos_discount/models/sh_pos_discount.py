# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.


from odoo import fields, models


class PosDiscount(models.Model):
    _name = 'sh.pos.discount'
    _description = 'Point of sale Discount'
    _rec_name = "sh_discount_name"

    sh_discount_name = fields.Char("Name")
    sh_discount_code = fields.Char("Code")
    sh_discount_value = fields.Float("Value(%)")

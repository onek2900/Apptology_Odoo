# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields, models


class Posconfig(models.Model):
    _inherit = "pos.config"

    sh_allow_order_line_discount = fields.Boolean("Allow Line Discount")
    sh_allow_global_discount = fields.Boolean("Allow Global Discount")

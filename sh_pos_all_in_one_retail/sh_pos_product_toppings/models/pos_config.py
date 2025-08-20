# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields, api, _

class PosConfigInherit(models.Model):
    _inherit = 'pos.config'

    sh_enable_toppings = fields.Boolean(string="Enable Toppings")
    sh_add_toppings_on_click_product = fields.Boolean(string="Add Topping when product add to cart")
    sh_allow_same_product_different_qty = fields.Boolean(string="Allow Same Product With Different Toppings")

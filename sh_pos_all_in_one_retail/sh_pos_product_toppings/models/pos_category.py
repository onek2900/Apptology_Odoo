# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
 
from asyncio import constants
from cmath import cos
from odoo import models, fields, api, _

class PosCategoryInherit(models.Model):
    _inherit = "pos.category"

    sh_product_topping_ids = fields.Many2many('product.product', string="Toppings", domain="[('available_in_pos', '=', True)]")

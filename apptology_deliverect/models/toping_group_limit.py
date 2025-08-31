# coding: utf-8

from odoo import models


class ShToppingGroup(models.Model):
    _inherit = 'sh.topping.group'
    # Limits now provided by sh_pos_product_toppings module. No extra fields here.
    pass

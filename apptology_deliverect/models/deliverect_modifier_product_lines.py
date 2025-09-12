# -*- coding: utf-8 -*-
from odoo import models, fields


class DeliverectModifierProductLines(models.Model):
    """Class for Modifier Product Lines"""
    _name = "deliverect.modifier.product.lines"

    product_id = fields.Many2one(
        "product.product",
        domain=[('sh_is_topping', '=', True)],
        string="Modifier Product",
        help="Name of the modifier"
    )
    cost = fields.Float(string="Cost", related="product_id.lst_price",help="price of the modifier")
    modifier_group_id = fields.Many2one("deliverect.modifier.group")

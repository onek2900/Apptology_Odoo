# -*- coding: UTF-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields


class ShProductProduct(models.Model):
    _inherit = 'product.product'

    category_id = fields.Many2one(
        "uom.category",
        "UOM Category",
        related="uom_id.category_id"
    )

# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields


class ShTopPosProduct(models.Model):
    _name = "sh.tsp.top.pos.product"
    _description = 'Top pos product persistence model to  used in snippet or any other places'
    _order = 'id asc'

    product_id = fields.Many2one(
        comodel_name="product.product", string="Product")
    qty = fields.Float(string='Qty Sold')

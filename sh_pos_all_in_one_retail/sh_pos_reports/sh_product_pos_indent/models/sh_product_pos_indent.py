# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from odoo import models, fields


class ProductPOSIndentReport(models.Model):
    _name = 'sh.product.pos.indent'
    _description = 'Product POS Indent'

    name = fields.Many2one(
        comodel_name='product.product', string='Product')
    quantity = fields.Float(string='Quantity')
    sh_partner_id = fields.Many2one(
        'res.partner', string='Customer')
    sh_category_id = fields.Many2one(
        'product.category', string='Category')
    

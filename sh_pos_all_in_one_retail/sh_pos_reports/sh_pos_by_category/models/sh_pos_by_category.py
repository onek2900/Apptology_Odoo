# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from odoo import fields, models


class POSByCategoryReport(models.Model):
    _name = 'sh.pos.by.category'
    _description = 'POS By Product Category'

    name = fields.Char(string='Number')
    date = fields.Date()
    sh_product_id = fields.Many2one(
        'product.product', string='Product', index=True, required=True)
    qty = fields.Float()
    discount = fields.Float(string="Discount(%)")
    price = fields.Monetary()
    sh_product_uom_id = fields.Many2one(
        'uom.uom', string='UOM', index=True,)
    tax = fields.Monetary()
    subtotal = fields.Monetary()
    total = fields.Monetary()
    sh_category_id = fields.Many2one(
        'pos.category', string='Category', index=True,)

    company_id = fields.Many2one('res.company', store=True, copy=False,
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id)
    currency_id = fields.Many2one('res.currency', string="Currency",
                                  related='company_id.currency_id')

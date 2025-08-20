# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from odoo import models, fields


class POSProductProfitReport(models.Model):
    _name = 'sh.pos.product.profit'
    _description = 'POS Product Profit'

    name = fields.Char(string='Order Number')
    order_date = fields.Date()
    product_id = fields.Many2one(
        'product.product', string='Product')
    quantity = fields.Float()
    profit = fields.Float()
    margin = fields.Float(string="Margin (%)")
    sh_partner_id = fields.Many2one(
        'res.partner', string='Customer')
    company_id = fields.Many2one('res.company', store=True, copy=False,
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id)
    currency_id = fields.Many2one('res.currency', string="Currency",
                                  related='company_id.currency_id')
    cost = fields.Monetary()
    sale_price = fields.Monetary()

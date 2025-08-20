# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from odoo import models, fields


class POSAnalysisOrderReport(models.Model):
    _name = 'sh.customer.pos.analysis.order'
    _description = 'Customer POS Analysis Order'

    name = fields.Char(string='Order Number')
    order_date = fields.Date()
    user_id = fields.Many2one(
        'res.users', string='Salesperson', index=True,)
    sh_partner_id = fields.Many2one(
        'res.partner', string='Customer', required=True)
    company_id = fields.Many2one('res.company', store=True, copy=False,
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id)
    currency_id = fields.Many2one('res.currency', string="Currency",
                                  related='company_id.currency_id')
    sales_amount = fields.Monetary()
    amount_paid = fields.Monetary()
    balance = fields.Monetary()


class POSAnalysisProductReport(models.Model):
    _name = 'sh.customer.pos.analysis.product'
    _description = 'Customer POS Analysis Product'

    name = fields.Char(string='Number')
    date = fields.Date()
    sh_partner_id = fields.Many2one(
        'res.partner', string='Customer', required=True)
    company_id = fields.Many2one('res.company', store=True, copy=False,
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id)
    currency_id = fields.Many2one('res.currency', string="Currency",
                                  related='company_id.currency_id')
    sh_product_id = fields.Many2one(
        comodel_name='product.product', string='Product')
    price = fields.Monetary()
    quantity = fields.Float()
    discount = fields.Float(string='Disc.(%)')
    tax = fields.Float()
    subtotal = fields.Monetary()

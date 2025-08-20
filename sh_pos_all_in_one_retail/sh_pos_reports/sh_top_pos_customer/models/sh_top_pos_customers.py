# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from odoo import models, fields


class TopPOSCustomerReport(models.Model):
    _name = 'sh.top.pos.customers'
    _description = 'Top POS Customers'

    name = fields.Many2one('res.partner', string='Customer')
    company_id = fields.Many2one('res.company', store=True, copy=False,
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id)
    currency_id = fields.Many2one('res.currency', string="Currency",
                                  related='company_id.currency_id')
    sales_amount = fields.Monetary()

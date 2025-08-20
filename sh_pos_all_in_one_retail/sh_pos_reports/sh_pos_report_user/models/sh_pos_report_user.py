# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from odoo import models, fields


class POSUserReport(models.Model):
    _name = 'sh.pos.report.user'
    _description = 'POS Report By User'

    name = fields.Char(string='Order Number')
    order_date = fields.Datetime()
    sh_partner_id = fields.Many2one(
        'res.partner', string='Customer')
    sh_user_id = fields.Many2one(
        'res.users', string='User')
    company_id = fields.Many2one('res.company', store=True, copy=False,
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id)
    currency_id = fields.Many2one('res.currency', string="Currency",
                                  related='company_id.currency_id')
    total = fields.Monetary()
    amount_invoiced = fields.Monetary(string="Amount Invoiced")
    amount_due = fields.Monetary(string="Amount Due")

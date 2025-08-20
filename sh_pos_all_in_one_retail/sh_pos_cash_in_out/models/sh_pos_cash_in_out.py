# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields, models, api


class ShCashInOut(models.Model):
    _name = 'sh.cash.in.out'
    _description = "Cash In Out"

    sh_transaction_type = fields.Selection(
        [('cash_in', 'Cash In'), ('cash_out', 'Cash Out')], string="Transaction Type",)
    sh_amount = fields.Float(string="Amount")
    sh_reason = fields.Char(string="Reason")
    sh_session = fields.Many2one('pos.session', string="Session")
    sh_date = fields.Datetime(
        string='Date', readonly=True, index=True, default=fields.Datetime.now)

    @api.model
    def try_cash_in_out(self, session, _type, amount, reason):
        if _type == 'in':
            self.env['sh.cash.in.out'].create(
                {'sh_amount': amount, 'sh_reason': reason, 'sh_session': session, 'sh_transaction_type': 'cash_in'})
        else:
            self.env['sh.cash.in.out'].create(
                {'sh_amount': amount, 'sh_reason': reason, 'sh_session': session, 'sh_transaction_type': 'cash_out'})

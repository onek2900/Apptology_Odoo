# -*- coding: utf-8 -*-

from odoo import fields, models, _


class Lead(models.Model):
    _inherit = 'crm.lead'

    actual_revenue = fields.Monetary(string='Actual Revenue', currency_field='company_currency' ,compute='_compute_actual_revenue')

    def _compute_actual_revenue(self):
        for lead in self:
            sale_orders = self.env['sale.order'].search(['&',
                                                         ('opportunity_id', '=', lead.id),
                                                         ('state', 'not in', ('draft', 'sent', 'cancel'))
                                                         ])
            invoices = sale_orders.mapped('invoice_ids')
            total_revenue = 0.0
            for inv in invoices:
                if inv.payment_state not in ['paid', 'partial','reversed']:
                    continue
                paid_amount = inv.amount_total - inv.amount_residual
                if inv.move_type == 'out_invoice':
                    total_revenue += paid_amount
                elif inv.move_type == 'out_refund':
                    total_revenue -= paid_amount
            lead.actual_revenue = total_revenue
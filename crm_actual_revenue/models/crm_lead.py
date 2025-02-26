# -*- coding: utf-8 -*-

from odoo import fields, models, _, api


class Lead(models.Model):
    _inherit = 'crm.lead'

    actual_revenue = fields.Monetary(string='Actual Revenue', currency_field='company_currency',
                                     compute='_compute_actual_revenue', store=True)
    billed_amount = fields.Monetary(string='Billed Amount', currency_field='company_currency',
                                  compute='_compute_billed_amount', store=True)

    @api.depends('expected_revenue','actual_revenue')
    def _compute_billed_amount(self):
        for lead in self:
            lead.billed_amount = lead.expected_revenue - lead.actual_revenue

    @api.depends('order_ids.invoice_ids', 'order_ids.invoice_ids.payment_state',
                 'order_ids.invoice_ids.amount_residual', 'order_ids.invoice_ids.move_type')
    def _compute_actual_revenue(self):
        for lead in self:
            sale_orders = self.env['sale.order'].search(['&',
                                                         ('opportunity_id', '=', lead.id),
                                                         ('state', 'not in', ('draft', 'sent', 'cancel'))
                                                         ])
            invoices = sale_orders.mapped('invoice_ids')
            total_revenue = 0.0
            for inv in invoices:
                if inv.payment_state not in ['paid', 'partial', 'reversed']:
                    continue
                paid_amount = inv.amount_total - inv.amount_residual
                if inv.move_type == 'out_invoice':
                    total_revenue += paid_amount
                elif inv.move_type == 'out_refund':
                    total_revenue -= paid_amount
            lead.actual_revenue = total_revenue

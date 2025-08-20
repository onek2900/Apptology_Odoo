# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields, api


class POSOrderLine(models.Model):
    _inherit = "pos.order.line"

    sh_product_cost = fields.Float(
        string="Cost", compute="_compute_cost_product", store=True)
    sh_profit = fields.Float(
        string="Profit", compute="_compute_profit", store=True)
    order_date = fields.Datetime(
        string="Order Date", related="order_id.date_order", store=True)
    sh_return_qty = fields.Float(
        string="Return Quantity", compute="_compute_return_qty", store=True, default=0.0)
    sh_return_rate = fields.Float(
        string="Return Rate", compute="_compute_return_rate", store=True)
    sh_profitability = fields.Float(
        string="Profitability", compute="_compute_profitability", store=True)
    price_subtotal = fields.Monetary(
        compute='_compute_amount', string='POS Value', readonly=True, store=True)
    sh_tax_amount = fields.Float(
        string="Tax Amount", compute='_compute_tax_amount', readonly=False, store=True)
    sh_tax_percentage = fields.Float(
        string="Tax Percentage", compute='_compute_tax_amount', readonly=False, store=True)
    discount = fields.Float(string='Discount (%)', default=0.0)
    sh_discount_amount = fields.Float(
        string="Discount Amount", compute='_compute_discount_amount', readonly=False, store=True)
    sh_margin = fields.Float(
        string="Margin ", compute='_compute_pos_order_line_margin', readonly=False, store=True)

    def search_sh_product_cost(self, operator, value):
        pos_order_line = self.env['pos.order.line']
        domain = [('sh_product_cost', operator, value)]
        order_lines = pos_order_line.sudo().search(domain).ids
        if order_lines:
            return [('id', 'in', order_lines)]
        else:
            return []

    @api.depends('tax_ids')
    def _compute_tax_amount(self):
        for rec in self:
            if rec.tax_ids:
                sh_tax_amount=rec.tax_ids.amount if len(rec.tax_ids)==1 else sum(rec.tax_ids.mapped('amount'))
                rec.sh_tax_amount = (sh_tax_amount *
                                     rec.price_subtotal) / 100
                rec.sh_tax_percentage = sh_tax_amount
            else:
                rec.sh_tax_amount = 0.0
                rec.sh_tax_percentage = 0.0

    @api.depends('price_subtotal_incl')
    def _compute_discount_amount(self):
        for rec in self:
            if rec.price_subtotal_incl > 0.0:
                rec.sh_discount_amount = (
                    rec.price_subtotal_incl * rec.discount) / 100
            else:
                rec.sh_discount_amount = 0.0

    @api.depends('sh_profit', 'sh_product_cost')
    def _compute_profitability(self):
        for rec in self:
            if rec.sh_product_cost > 0.0:
                rec.sh_profitability = (
                    rec.sh_profit / rec.sh_product_cost) * 100
            else:
                rec.sh_profitability = 0.0

    @api.depends('qty', 'sh_return_qty')
    def _compute_return_rate(self):
        for rec in self:
            if rec.sh_return_qty > 0.0:
                rec.sh_return_rate = rec.price_unit
            else:
                rec.sh_return_rate = 0.0

    @api.depends('qty')
    def _compute_return_qty(self):
        for rec in self:
            if rec.qty < 0.0:
                rec.sh_return_qty += (rec.qty) * (-1)
            else:
                rec.sh_return_qty = 0.0

    @api.depends('product_id', 'qty')
    def _compute_cost_product(self):
        for rec in self:
            rec.sh_product_cost = rec.product_id.standard_price * rec.qty

    @api.depends('sh_product_cost', 'price_subtotal_incl')
    def _compute_profit(self):
        for rec in self:
            rec.sh_profit = rec.price_subtotal_incl - rec.sh_product_cost

    @api.depends('price_unit')
    def _compute_pos_order_line_margin(self):
        for rec in self:
            if rec.qty > 0.0:
                rec.sh_margin = (rec.price_unit - rec.product_id.standard_price)
            else:
                rec.sh_margin = -(rec.price_unit - rec.product_id.standard_price)

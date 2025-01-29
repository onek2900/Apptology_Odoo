# -*- coding: utf-8 -*-
from odoo import fields, models, api


class ProductTemplate(models.Model):
    """
        Inherit the product template model to introduce a total price field
        that shows tax included price.
    """
    _inherit = 'product.template'

    total_price = fields.Float(
        string="Total Price(Including VAT)",
        compute='_compute_total_price',
        inverse='_inverse_total_price',
        store=True,
        digits=(16, 4),
        help="Total price including taxes. This price will be used in POS."
    )

    @api.depends('list_price', 'taxes_id')
    def _compute_total_price(self):
        """
        When list_price changes, compute the total price with taxes.
        """
        for product in self:
            if not product.taxes_id:
                product.total_price = product.list_price
            else:
                taxes = product.taxes_id.compute_all(
                    product.list_price,
                    currency=product.currency_id,
                    quantity=1.0,
                    product=product,
                    partner=self.env['res.partner']
                )
                product.total_price = taxes['total_included']

    def _inverse_total_price(self):
        """
        When total_price is modified, compute and update list_price.
        """
        for product in self:
            if not product.taxes_id:
                product.list_price = product.total_price
            else:
                tax_factor = 1.0
                for tax in product.taxes_id:
                    if tax.amount_type == 'percent':
                        tax_factor += tax.amount / 100.0
                product.list_price = product.total_price / tax_factor

    @api.onchange('total_price')
    def _onchange_total_price(self):
        """
        Instantly update list_price when total_price changes in the UI.
        """
        if not self.taxes_id:
            self.list_price = self.total_price
        else:
            tax_factor = 1.0
            for tax in self.taxes_id:
                if tax.amount_type == 'percent':
                    tax_factor += tax.amount / 100.0
            self.list_price = self.total_price / tax_factor

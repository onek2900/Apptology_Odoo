# -*- coding: utf-8 -*-
from odoo import fields, models, api


class ProductProduct(models.Model):
    """
    Inherit the product variant model to introduce a total price field
    that shows tax included price at variant level.
    """
    _inherit = 'product.product'

    variant_total_price = fields.Float(
        string="Total Price(Including VAT)",
        compute='_compute_variant_total_price',
        inverse='_inverse_variant_total_price',
        store=True,
        digits=(16, 4),
        help="Total price including taxes for this specific variant. This price will be used in POS."
    )

    @api.depends('lst_price', 'taxes_id', 'product_tmpl_id.total_price')
    def _compute_variant_total_price(self):
        """
        Compute the total price with taxes for variants.
        """
        for product in self:
            if not product.taxes_id:
                product.variant_total_price = product.lst_price
            else:
                taxes = product.taxes_id.compute_all(
                    product.lst_price,
                    currency=product.currency_id,
                    quantity=1.0,
                    product=product,
                    partner=self.env['res.partner']
                )
                product.variant_total_price = taxes['total_included']

    def _inverse_variant_total_price(self):
        """
        When variant_total_price is modified, compute and update lst_price.
        """
        for product in self:
            if not product.taxes_id:
                product.lst_price = product.variant_total_price
            else:
                tax_factor = 1.0
                for tax in product.taxes_id:
                    if tax.amount_type == 'percent':
                        tax_factor += tax.amount / 100.0
                product.lst_price = product.variant_total_price / tax_factor

    @api.onchange('variant_total_price')
    def _onchange_variant_total_price(self):
        """
        Instantly update lst_price when variant_total_price changes in the UI.
        """
        if not self.taxes_id:
            self.lst_price = self.variant_total_price
        else:
            tax_factor = 1.0
            for tax in self.taxes_id:
                if tax.amount_type == 'percent':
                    tax_factor += tax.amount / 100.0
            self.lst_price = self.variant_total_price / tax_factor

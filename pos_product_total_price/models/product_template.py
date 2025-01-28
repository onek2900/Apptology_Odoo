# -*- coding: utf-8 -*-
from odoo import fields, models, api


class ProductTemplate(models.Model):
    """
        Inherit the product template model to introduce a total price field
        that shows tax included price.
    """
    _inherit = 'product.template'

    total_price = fields.Float(
        string="Total Price",
        digits='Product Price',
        help="Total price of the product including applicable taxes."
    )

    @api.onchange('list_price', 'taxes_id')
    def _onchange_list_price(self):
        """
            Compute and update the total price of the product when either the
            list price or associated taxes are modified.
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

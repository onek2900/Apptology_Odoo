# -*- coding: utf-8 -*-

from collections import defaultdict
from odoo import api, models


class POSSession(models.Model):
    """
    A model extending POS sessions to retrieve aggregated product quantities.
    Provides methods for fetching session-specific product sales details.
    """
    _inherit = 'pos.session'

    @api.model
    def get_session_products(self, session_id):
        """
        Get aggregated product quantities for a given POS session.
        """
        session_orders = self.env['pos.order'].search(
            [('session_id', '=', session_id)]).ids
        session_order_lines = self.env['pos.order.line'].search(
            [('order_id', 'in', session_orders)])
        product_details = defaultdict(lambda: {'quantity': 0, 'total': 0.0})

        for line in session_order_lines:
            product = line.product_id
            product_details[product.id]['quantity'] += line.qty
            product_details[product.id]['total'] += line.price_subtotal_incl
            product_details[product.id]['product_name'] = product.display_name
        product_list = [
            {
                'product_name': details['product_name'],
                'quantity': details['quantity'],
                'total': details['total']
            }
            for details in product_details.values()
        ]
        for product in product_list:
            product['total'] = round(product['total'], 2)
        return product_list


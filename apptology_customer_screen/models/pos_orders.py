# -*- coding: utf-8 -*-

from odoo import models
from odoo.http import request


class PosOrder(models.Model):
    """Inheriting the pos order model"""
    _inherit = "pos.order"

    def trigger_bus(self, order_details):
        order_name = order_details[0].get('order_name') if order_details else ""
        currency_symbol = order_details[0].get(
            'currency_symbol') if order_details else ""
        product_list = []
        for line in order_details:
            price = line.get('price', 0)
            quantity = line.get('quantity', 0)
            tax_ids = line.get('tax_ids', [])
            product_name = line.get('product_name', '')
            product_id = line.get('product_id', '')
            discount = line.get('discount')
            image_1024 = request.env['product.product'].sudo().browse(product_id).image_1024
            # Fetch taxes
            taxes = self.env['account.tax'].sudo().browse(tax_ids)

            # Calculate total tax
            total_tax = 0
            for tax in taxes:
                if tax.amount_type == 'percent':
                    tax_amount = price * (tax.amount / 100)
                elif tax.amount_type == 'fixed':
                    tax_amount = tax.amount
                else:
                    tax_amount = 0
                total_tax += tax_amount

            # Calculate total price before discount
            total_price = (price + total_tax) * quantity

            # Apply discount (as a percentage reduction)
            discount_amount = (total_price * discount) / 100
            total_price -= discount_amount  # Deduct discount from total price

            # Round values to 2 decimal places
            quantity = round(quantity, 2)
            total_price = round(total_price, 2)

            product_list.append(
                {
                    'quantity': quantity,
                    'total_price': round(total_price, 2),
                    'product_name': product_name,
                    'product_id': product_id,
                    'product_image':image_1024,
                })
        total_amount = round(sum(
            line.get('total_price', 0) for line in product_list), 2)
        message = {
            'res_model': self._name,
            'message': 'pos_order_line_updated',
            'orders': product_list,
            'order_name': order_name,
            'currency_symbol':currency_symbol,
            'total_amount': total_amount,
            'channel': "test_channel_first"
        }
        channel = "test_channel_first"
        self.env["bus.bus"]._sendone(channel, "notification", message)
        return True

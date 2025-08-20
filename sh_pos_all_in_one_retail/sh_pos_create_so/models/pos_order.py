# Copyright (C) Softhealer Technologies.
# Part of Softhealer Technologies.

from odoo import models, api


class SaleOrderInherit(models.Model):
    _inherit = "pos.order"

    @api.model
    def sh_create_sale_order(self, vals, is_confirm):
        templst = []
        for order in vals:
            create_vals = {
                "partner_id": order.get("partner_id"),
                "payment_term_id": order.get("payment_term_id"),
                "order_line": [],
            }
            for line in order.get("order_lines"):
                line_val = {
                    "product_uom_qty": line.get("qty"),
                    "price_unit": line.get("price_unit"),
                    "price_subtotal": line.get("price_subtotal"),
                    "product_id": line.get("product_id"),
                    "name": line.get("full_product_name"),
                    "tax_id": line.get("tax_ids"),
                }
                create_vals.get("order_line").append((0, 0, line_val))

            created = self.env['sale.order'].create(create_vals)
            if is_confirm and is_confirm == "confirm":
                created.action_confirm()
            templst.append(created.read()[0])

        return templst

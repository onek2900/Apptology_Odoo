# Copyright (C) Softhealer Technologies.
# Part of Softhealer Technologies.


from odoo import models, fields, api


class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    product_weight = fields.Float(string="Weight (kg)")
    product_volume = fields.Float(string="Volume (m³)")
    total_product_weight = fields.Float(string="Total Weight (kg)")
    total_product_volume = fields.Float(string="Total Volume (m³)")


class PosOrder(models.Model):
    _inherit = "pos.order"

    enable_product_weight = fields.Boolean(related="config_id.enable_weight")
    enable_product_volume = fields.Boolean(related="config_id.enable_volume")
    total_product_weight = fields.Float(string="Total Weight (kg)")
    total_product_volume = fields.Float(string="Total Volume (m³)")

    @api.model
    def _order_fields(self, ui_order):
        res = super()._order_fields(ui_order)

        res["total_product_weight"] = ui_order.get("total_product_weight", False)
        res["total_product_volume"] = ui_order.get("total_product_volume", False)

        return res

# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from odoo import models, fields, api


class ShResConfig(models.TransientModel):
    _inherit = "res.config.settings"

    enable_order_type = fields.Boolean(
        related="pos_config_id.enable_order_type", readonly=False
    )
    order_type_mode = fields.Selection(
        related="pos_config_id.order_type_mode", readonly=False
    )
    order_types_ids = fields.Many2many(
        comodel_name="sh.order.type",
        related="pos_config_id.order_types_ids",
        readonly=False,
    )
    order_type_id = fields.Many2one(
        related="pos_config_id.order_type_id", readonly=False
    )

    @api.onchange("order_type_mode", "order_types_ids")
    def _onchange_order_type_mode(self):
        if self.order_type_mode == "multi":
            return {
                "domain": {
                    "order_type_id": [
                        ("id", "in", self.order_types_ids._origin.mapped("id"))
                    ]
                }
            }
        else:
            return {"domain": {"order_type_id": []}}

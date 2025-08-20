# Copyright (C) Softhealer Technologies.
# Part of Softhealer Technologies.

from odoo import models


class PosSessionInherit(models.Model):
    _inherit = "pos.session"

    # pos.product.template
    def _pos_ui_models_to_load(self):
        result = super()._pos_ui_models_to_load()

        if "pos.product.template" not in result:
            result.append("pos.product.template")

        if "pos.product.template.line" not in result:
            result.append("pos.product.template.line")

        return result

    def _loader_params_pos_product_template(self):
        return {
            "search_params": {
                "domain": [("active", "=", True)],
                "fields": ["name", "amount_total", "pos_product_template_ids"],
                "load": False,
            }
        }

    def _get_pos_ui_pos_product_template(self, params):
        return self.env["pos.product.template"].search_read(**params["search_params"])

    # pos.product.template.line

    def _loader_params_pos_product_template_line(self):
        return {
            "search_params": {
                "domain": [],
                "fields": [
                    "name",
                    "description",
                    "ordered_qty",
                    "unit_price",
                    "discount",
                    "product_uom",
                    "price_subtotal",
                    "pos_template_id",
                ],
                "load": False,
            }
        }

    def _get_pos_ui_pos_product_template_line(self, params):
        return self.env["pos.product.template.line"].search_read(
            **params["search_params"]
        )

    def _pos_data_process(self, loaded_data):
        super()._pos_data_process(loaded_data)

# Part of Softhealer Technologies.

from odoo import models, fields


class ResConfigSettiongsInhert(models.TransientModel):
    _inherit = "res.config.settings"

    enable_order_line_label = fields.Boolean(
        related="pos_config_id.enable_order_line_label", readonly=False)
    enabel_delete_label_with_product = fields.Boolean(
        related="pos_config_id.enabel_delete_label_with_product", readonly=False)
    enable_order_line_label_in_receipt = fields.Boolean(
        related="pos_config_id.enable_order_line_label_in_receipt", readonly=False)

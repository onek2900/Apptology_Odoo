# Copyright (C) Softhealer Technologies.
# Part of Softhealer Technologies.


from odoo import models, fields


class ResConfigSettiongsInhert(models.TransientModel):
    _inherit = "res.config.settings"

    pos_enable_weight = fields.Boolean(
        related="pos_config_id.enable_weight", readonly=False
    )
    pos_enable_volume = fields.Boolean(
        related="pos_config_id.enable_volume", readonly=False
    )
    pos_product_weight_receipt = fields.Boolean(
        related="pos_config_id.product_weight_receipt", readonly=False
    )
    pos_product_volume_receipt = fields.Boolean(
        related="pos_config_id.product_volume_receipt", readonly=False
    )

# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models, fields


class ResConfigSettiongsInhert(models.TransientModel):
    _inherit = "res.config.settings"

    pos_sh_pos_enable_product_variants = fields.Boolean(
        related="pos_config_id.sh_pos_enable_product_variants", readonly=False)
    pos_sh_close_popup_after_single_selection = fields.Boolean(
        related="pos_config_id.sh_close_popup_after_single_selection", readonly=False)
    pos_sh_pos_display_alternative_products = fields.Boolean(
        related="pos_config_id.sh_pos_display_alternative_products", readonly=False)
    pos_sh_pos_variants_group_by_attribute = fields.Boolean(
        related="pos_config_id.sh_pos_variants_group_by_attribute", readonly=False)

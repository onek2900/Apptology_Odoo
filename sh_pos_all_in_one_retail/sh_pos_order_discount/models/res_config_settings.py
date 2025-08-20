# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    pos_sh_allow_order_line_discount = fields.Boolean(
        related="pos_config_id.sh_allow_order_line_discount",
        string="Allow Line Discount",
        readonly=False,
    )
    pos_sh_allow_global_discount = fields.Boolean(
        related="pos_config_id.sh_allow_global_discount",
        string="Allow Global Discount",
        readonly=False,
    )

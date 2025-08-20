# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    pos_sh_enable_shortcut = fields.Boolean(
        related="pos_config_id.sh_enable_shortcut",
        string="Enable Shortcut Key",
        readonly=False,
    )
    pos_sh_shortcut_keys_screen = fields.One2many(
        related="pos_config_id.sh_shortcut_keys_screen",
        string="POS Shortcut Key",
        readonly=False,
    )
    pos_sh_payment_shortcut_keys_screen = fields.One2many(
        related="pos_config_id.sh_payment_shortcut_keys_screen",
        string="POS Payment Method Shortcut Key",
        readonly=False,
    )

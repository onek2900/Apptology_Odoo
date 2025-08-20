# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields, models


class PosConfig(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_sh_enable_cash_in_out_statement = fields.Boolean(
        related="pos_config_id.sh_enable_cash_in_out_statement", readonly=False)
    pos_sh_enable_payment = fields.Boolean(
        related="pos_config_id.sh_enable_payment", readonly=False)

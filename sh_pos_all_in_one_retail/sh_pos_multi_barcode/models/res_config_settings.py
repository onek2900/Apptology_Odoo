# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models, fields, api


class ResConfigSettiongsInhert(models.TransientModel):
    _inherit = "res.config.settings"

    pos_sh_enable_multi_barcode = fields.Boolean(
        related="pos_config_id.sh_enable_multi_barcode", readonly=False)

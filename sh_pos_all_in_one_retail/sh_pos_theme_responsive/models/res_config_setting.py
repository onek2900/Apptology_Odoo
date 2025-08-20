# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import  fields, models


class ShResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_sh_pos_night_mode = fields.Boolean(related='pos_config_id.sh_pos_night_mode', readonly=False)
   
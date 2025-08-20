# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields, models

class ShPosConfig(models.Model):
    _inherit = 'pos.config'

    sh_pos_night_mode = fields.Boolean(string="Enable Night Mode")

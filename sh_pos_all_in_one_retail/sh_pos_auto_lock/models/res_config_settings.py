# Copyright (C) Softhealer Technologies.
# Part of Softhealer Technologies.

from odoo import models, fields


class ResConfigInherit(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_sh_enable_auto_lock = fields.Boolean(
        related="pos_config_id.sh_enable_auto_lock", readonly=False)
    pos_sh_lock_timer = fields.Integer(
        related="pos_config_id.sh_lock_timer", readonly=False)

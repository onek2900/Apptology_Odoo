# Copyright (C) Softhealer Technologies.
# Part of Softhealer Technologies.

from odoo import models, fields


class ResConfigInherit(models.TransientModel):
    _inherit = 'res.config.settings'

    sh_apply_custom_discount = fields.Boolean(
        related="pos_config_id.sh_apply_custom_discount", readonly=False)
    sh_apply_both_discount = fields.Boolean(
        related="pos_config_id.sh_apply_both_discount", readonly=False)

# Copyright (C) Softhealer Technologies.
# Part of Softhealer Technologies.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_sh_pricelist_for_code = fields.Many2one(
        related="pos_config_id.sh_pricelist_for_code", readonly=False)
    pos_sh_min_pricelist_value = fields.Many2one(
        related="pos_config_id.sh_min_pricelist_value", readonly=False)

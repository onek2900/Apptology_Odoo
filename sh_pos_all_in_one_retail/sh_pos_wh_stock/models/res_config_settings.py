# Copyright (C) Softhealer Technologies.
# Part of Softhealer Technologies.

from odoo import models, fields


class posConfigInherit(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_sh_display_stock = fields.Boolean(
        related="pos_config_id.sh_display_stock", readonly=False)
    pos_sh_display_by = fields.Selection(
        related="pos_config_id.sh_display_by", readonly=False)
    pos_sh_min_qty = fields.Integer(
        related="pos_config_id.sh_min_qty", readonly=False)
    pos_sh_show_qty_location = fields.Boolean(
        related="pos_config_id.sh_show_qty_location", readonly=False)
    pos_sh_pos_location = fields.Many2one(
        related="pos_config_id.sh_pos_location", readonly=False)

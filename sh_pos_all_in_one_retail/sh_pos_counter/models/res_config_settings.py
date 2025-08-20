# Copyright (C) Softhealer Technologies.
from odoo import fields, models

class ResConfigSettiongsInhert(models.TransientModel):
    _inherit = "res.config.settings"

    pos_enable_pos_item_counter = fields.Boolean(
        related="pos_config_id.enable_pos_item_counter", readonly=False)
    pos_enable_pos_qty_counter = fields.Boolean(
        related="pos_config_id.enable_pos_qty_counter", readonly=False)
    pos_enable_pos_item_report = fields.Boolean(
        related="pos_config_id.enable_pos_item_report", readonly=False)
    pos_enable_pos_qty_report = fields.Boolean(
        related="pos_config_id.enable_pos_qty_report", readonly=False)

# Copyright (C) Softhealer Technologies.
from odoo import fields, models

class ResConfigSettiongsInhert(models.TransientModel):
    _inherit = "res.config.settings"

    pos_enable_orderline_note = fields.Boolean(related="pos_config_id.enable_orderline_note", readonly=False)
    pos_enable_order_note = fields.Boolean(related="pos_config_id.enable_order_note", readonly=False)
    pos_display_orderline_note_receipt = fields.Boolean(related="pos_config_id.display_orderline_note_receipt", readonly=False)
    pos_display_order_note_receipt = fields.Boolean(related="pos_config_id.display_order_note_receipt", readonly=False)
    pos_display_order_note_payment = fields.Boolean(related="pos_config_id.display_order_note_payment", readonly=False)
    pos_hide_extra_note_checkbox = fields.Boolean(related="pos_config_id.hide_extra_note_checkbox", readonly=False)

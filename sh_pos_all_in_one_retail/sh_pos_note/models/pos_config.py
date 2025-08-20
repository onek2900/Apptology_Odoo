# Copyright (C) Softhealer Technologies.
from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    enable_orderline_note = fields.Boolean(
        "Enable OrderLine Note", default=False)
    enable_order_note = fields.Boolean(
        "Enable Global Note", default=False)
    display_orderline_note_receipt = fields.Boolean(
        "Display Line Note in Receipt")
    display_order_note_receipt = fields.Boolean(
        "Display Global Note in Receipt")
    display_order_note_payment = fields.Boolean(
        "Display Global Note in Payment")
    hide_extra_note_checkbox = fields.Boolean(string = "Hide Store Extra Note")

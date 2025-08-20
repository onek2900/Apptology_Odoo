# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.
from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    select_uom_type = fields.Selection([('primary', 'Primary'), (
        'secondary', 'Secondary')], string='Select Default UOM type', default='primary')
    display_uom_in_receipt = fields.Boolean(string='Display UOM in Receipt')
    enable_price_to_display = fields.Boolean(
        string='Display price in Secondary UOM ?')

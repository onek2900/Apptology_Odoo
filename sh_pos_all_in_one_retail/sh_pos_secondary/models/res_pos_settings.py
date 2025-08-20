# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.
from odoo import fields, models


class POSOrderLine(models.Model):
    _inherit = 'pos.order.line'

    secondary_qty = fields.Float("Secondary Qty")
    secondary_uom_id = fields.Many2one('uom.uom', string="Secondary UOM")


class ResConfigInherit(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_display_uom_in_receipt = fields.Boolean(
        related="pos_config_id.display_uom_in_receipt", readonly=False)
    pos_enable_price_to_display = fields.Boolean(
        related="pos_config_id.enable_price_to_display", readonly=False)
    pos_select_uom_type = fields.Selection(
        related="pos_config_id.select_uom_type", readonly=False)

# Copyright (C) Softhealer Technologies.
# Part of Softhealer Technologies.

from odoo import models, fields

class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    add_section = fields.Char(string='Section')

    def _export_for_ui(self, orderline):
        result = super()._export_for_ui(orderline)
        result['add_section'] = orderline.add_section
        return result

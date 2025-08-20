# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from odoo import fields, models, api


class PosOrder(models.Model):
    _inherit = 'pos.order'

    sh_order_type_id = fields.Many2one('sh.order.type', string='Order Type')

    @api.model
    def _order_fields(self, ui_order):
        res = super()._order_fields(ui_order)
        res['sh_order_type_id'] = ui_order.get('sh_order_type_id', False)
        return res

# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from odoo import models, fields,api


class ShPosConfig(models.Model):
    _inherit = 'pos.config'

    enable_order_type = fields.Boolean(string='Enable Order Type')
    order_type_mode = fields.Selection(string='Order type mode', selection=[
                                       ('single', 'Single'), ('multi', 'Multiple'), ])
    order_types_ids = fields.Many2many('sh.order.type', string='Order Types')
    order_type_id = fields.Many2one(
        'sh.order.type', string='Default Order Type')
    

    @api.onchange('order_type_mode', 'order_types_ids')
    def _onchange_order_type_mode(self):
        if self.order_type_mode == 'multi':
            return {'domain': {'order_type_id': [('id', 'in', self.order_types_ids._origin.mapped('id'))]}}
        else:
            return {'domain': {'order_type_id': []}}
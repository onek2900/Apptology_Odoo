# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields, api, _

class PosOrderlineInherit(models.Model):
    _inherit = 'pos.order.line'

    sh_is_has_topping = fields.Boolean(string="Has Topping")
    sh_is_topping = fields.Boolean(string="is Topping")

    def _export_for_ui(self, orderline):
        result = super(PosOrderlineInherit, self)._export_for_ui(orderline)

        result['sh_is_has_topping'] = orderline.sh_is_has_topping,
        result['sh_is_topping'] = orderline.sh_is_topping,
        return result
        
class PosOrderInherit(models.Model):
    _inherit = 'pos.order'

    def _get_fields_for_order_line(self):
        fields = super(PosOrderInherit, self)._get_fields_for_order_line()
        fields.extend(['sh_is_has_topping', 'sh_is_topping'])
        
        return fields
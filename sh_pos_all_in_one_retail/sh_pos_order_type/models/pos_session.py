# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from odoo import models


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _pos_ui_models_to_load(self):
        result = super()._pos_ui_models_to_load()
        result.append('sh.order.type')
        return result
    def _loader_params_sh_order_type(self):
        if self.config_id.enable_order_type and self.config_id.order_type_mode == 'multi':
            selected_types = self.config_id.order_types_ids.mapped('id')
            domain = [('id', 'in', selected_types)]
        elif self.config_id.enable_order_type and self.config_id.order_type_mode != 'multi' and self.config_id.order_type_id:
            domain = [('id', '=', self.config_id.order_type_id.id)]
        else:
            domain = [('id', '=', False)]
        return {
            'search_params': {
                'domain': domain,
                'fields': ['name', 'is_home_delivery','img'],
            }
        }

    def _get_pos_ui_sh_order_type(self, params):
        return self.env['sh.order.type'].search_read(**params['search_params'])

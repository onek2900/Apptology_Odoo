# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models


class PosSessionInherit(models.Model):
    _inherit = 'pos.session'

    def _pos_ui_models_to_load(self):
        result = super()._pos_ui_models_to_load()
        if 'sh.pos.discount' not in result:
            result.append('sh.pos.discount')
        return result

    def _loader_params_sh_pos_discount(self):
        return {'search_params': {'domain': [], 'fields': [], 'load': False}}

    def _get_pos_ui_sh_pos_discount(self, params):
        return self.env['sh.pos.discount'].search_read(**params['search_params'])

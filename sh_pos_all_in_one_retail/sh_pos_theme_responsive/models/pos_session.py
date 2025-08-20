# Copyright (C) Softhealer Technologies.
# Part of Softhealer Technologies.

from odoo import models


class PosSessionInherit(models.Model):
    _inherit = "pos.session"

    def _loader_params_product_product(self):
        result = super(PosSessionInherit,
                       self)._loader_params_product_product()
        result['search_params']['fields'].extend(
            ["type", "qty_available", "virtual_available"])
        return result

    def _pos_data_process(self, loaded_data):
        super()._pos_data_process(loaded_data)
        loaded_data['pos_theme_settings_data_by_theme_id'] = {
            sh_theme['id']: sh_theme for sh_theme in loaded_data['sh.pos.theme.settings']}

    def _pos_ui_models_to_load(self):
        result = super()._pos_ui_models_to_load()
        new_model = 'sh.pos.theme.settings'
        if new_model not in result:
            result.append(new_model)
        return result

    def _loader_params_sh_pos_theme_settings(self):
        return {'search_params': {'domain': [], 'fields': [], 'load': False}}

    def _get_pos_ui_sh_pos_theme_settings(self, params):
        return self.env['sh.pos.theme.settings'].search_read(**params['search_params'])

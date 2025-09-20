# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields, api, _


class PosSessionInherit(models.Model):
    _inherit = "pos.session"

    def _loader_params_product_product(self):
        result = super(PosSessionInherit,self)._loader_params_product_product()
        result['search_params']['fields'].extend([
            'sh_topping_ids',
            'sh_is_global_topping',
            'sh_topping_group_ids',
            'sh_topping_sequence',
            'sh_is_topping',
        ])
        return result
    
    def _loader_params_pos_category(self):
        result = super(PosSessionInherit,self)._loader_params_pos_category()
        result['search_params']['fields'].append('sh_product_topping_ids')
        return result

    # Load topping groups into the POS UI so the frontend can group toppings
    def _pos_ui_models_to_load(self):
        result = super()._pos_ui_models_to_load()
        if 'sh.topping.group' not in result:
            result.append('sh.topping.group')
        return result

    def _loader_params_sh_topping_group(self):
        fields = ['name', 'toppinds_ids', 'sequence']
        # Include optional fields if they exist (e.g., from apptology_deliverect)
        group_model = self.env['sh.topping.group']
        for opt in ['min', 'max', 'multi_max']:
            if opt in group_model._fields:
                fields.append(opt)
        return {'search_params': {'domain': [], 'fields': fields, 'load': True}}

    def _get_pos_ui_sh_topping_group(self, params):
        return self.env['sh.topping.group'].search_read(**params['search_params'])

    def _pos_data_process(self, loaded_data):
        super()._pos_data_process(loaded_data)
        # Build helper index for quick access by id on the frontend
        if loaded_data.get('sh.topping.group'):
            loaded_data['topping_groups_by_id'] = {
                grp['id']: grp for grp in loaded_data['sh.topping.group']
            }

# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models


class PosSessionInherit(models.Model):
    _inherit = 'pos.session'

    def _loader_params_product_product(self):
        result = super()._loader_params_product_product()
        result['search_params']['fields'].extend(['sh_alternative_products', 'name', 'product_template_attribute_value_ids', 'product_variant_count'])
        return result

    def _pos_data_process(self, loaded_data):
        super()._pos_data_process(loaded_data)
        loaded_data['attribute_by_id'] = {data['id']: data for data in loaded_data['product.template.attribute.line']}
        loaded_data['attribute_value_by_id'] = {data['id']: data for data in loaded_data['product.template.attribute.value']}
        
    def _pos_ui_models_to_load(self):
        result = super()._pos_ui_models_to_load()
        if 'product.template.attribute.line' not in result:
            result.append('product.template.attribute.line')
        if 'product.template.attribute.value' not in result:
            result.append('product.template.attribute.value')
        return result

    def _loader_params_product_template_attribute_line(self):
        return {'search_params': {'domain': [], 'fields': [], 'load': False}}

    def _get_pos_ui_product_template_attribute_line(self, params):
        return self.env['product.template.attribute.line'].search_read(**params['search_params'])

    def _loader_params_product_template_attribute_value(self):
        return {'search_params': {'domain': [], 'fields': [], 'load': False}}

    def _get_pos_ui_product_template_attribute_value(self, params):
        return self.env['product.template.attribute.value'].search_read(**params['search_params'])

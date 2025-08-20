# Copyright (C) Softhealer Technologies.
# Part of Softhealer Technologies.

from odoo import models

class PosSessionInherit(models.Model):
    _inherit = "pos.session"

    def _pos_ui_models_to_load(self):
        result = super()._pos_ui_models_to_load()
        if 'product.suggestion' not in result:
            result.append('product.suggestion')
        if 'sh.uom.line' not in result:
            result.append('sh.uom.line')
        return result

    def _loader_params_product_suggestion(self):
        return {'search_params': {'domain': [], 'fields': [], 'load': False}}

    def _get_pos_ui_product_suggestion(self, params):
        return self.env['product.suggestion'].search_read(**params['search_params'])

    def _loader_params_sh_uom_line(self):
        return {'search_params': {'domain': [], 'fields': [], 'load': False}}

    def _get_pos_ui_sh_uom_line(self, params):
        return self.env['sh.uom.line'].search_read(**params['search_params'])
    
    def _loader_params_product_product(self):
        result = super()._loader_params_product_product()
        result['search_params']['fields'].append('suggestion_line')
        result['search_params']['fields'].append('sh_uom_line_ids')
        return result

    def _product_pricelist_item_fields(self):
        return super()._product_pricelist_item_fields() + ["sh_uom_id"]

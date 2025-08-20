# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields, api, _


class PosSessionInherit(models.Model):
    _inherit = "pos.session"

    def _loader_params_product_product(self):
        result = super(PosSessionInherit,self)._loader_params_product_product()
        result['search_params']['fields'].extend(['sh_topping_ids','sh_is_global_topping','sh_topping_group_ids'])
        return result
    
    def _loader_params_pos_category(self):
        result = super(PosSessionInherit,self)._loader_params_pos_category()
        result['search_params']['fields'].append('sh_product_topping_ids')
        return result
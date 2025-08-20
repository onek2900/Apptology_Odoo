# Copyright (C) Softhealer Technologies.
# Part of Softhealer Technologies.

from odoo import models,fields

class PosSessionInherit(models.Model):
    _inherit = "pos.session"

    def _loader_params_res_users(self):
        result = super(PosSessionInherit,self)._loader_params_res_users()
        result['search_params']['fields'].append('sign')
        return result
    
    def _loader_params_res_partner(self):
        result = super(PosSessionInherit,self)._loader_params_res_partner()
        result['search_params']['fields'].extend(["lang", "mobile"])
        return result
        
        
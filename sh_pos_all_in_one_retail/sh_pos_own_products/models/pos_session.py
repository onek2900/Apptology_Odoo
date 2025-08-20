from odoo import models,fields

class PosSessionInherit(models.Model):
    _inherit = "pos.session"

    def _loader_params_product_product(self):
        result = super(PosSessionInherit,self)._loader_params_product_product()
        result['search_params']['fields'].append('sh_select_user')
        return result
    
    def _loader_params_product_template(self):
        result = super(PosSessionInherit,self)._loader_params_product_template()
        result['search_params']['fields'].append('sh_select_user')
        return result

from odoo import models,fields

class PosSessionInherit(models.Model):
    _inherit = "pos.session"

    def _loader_params_res_partner(self):
        result = super(PosSessionInherit,self)._loader_params_res_partner()
        result['search_params']['fields'].append('sh_own_customer')
        return result


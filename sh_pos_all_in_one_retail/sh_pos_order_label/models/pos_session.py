# Copyright (C) Softhealer Technologies.
# Part of Softhealer Technologies.

from odoo import models

class PosSession(models.Model):
    _inherit = 'pos.session'

    def _loader_params_product_product(self):
        result = super(PosSession, self)._loader_params_product_product()
        result['search_params']['fields'].append('sh_order_label_demo_product')
        return result
    
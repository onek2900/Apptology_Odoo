# Copyright (C) Softhealer Technologies.
# Part of Softhealer Technologies.

from odoo import models, fields


class PosSession(models.Model):
    _inherit = "pos.session"

    def _loader_params_res_users(self):
        result = super(PosSession,
                       self)._loader_params_res_users()
        result['search_params']['fields'].append('sh_is_direct_logout')
        return result

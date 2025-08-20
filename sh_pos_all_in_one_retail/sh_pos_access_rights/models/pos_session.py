# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models

class PosSession(models.Model):
    _inherit = 'pos.session'

    def _get_pos_ui_res_users(self, params):
        user = self.env['res.users'].search_read(**params['search_params'])[0]
        user['role'] = 'manager' if any(id == self.config_id.group_pos_manager_id.id for id in user['groups_id']) else 'cashier'
        return user

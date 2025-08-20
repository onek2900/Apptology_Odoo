# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models, fields


class ResUsers(models.Model):
    _inherit = "res.users"

    pos_config_id = fields.Many2one("pos.config", string="POS Config")
    sh_is_direct_logout = fields.Boolean(string="Is Direct LogOut ?")

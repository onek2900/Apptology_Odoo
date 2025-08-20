# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields, api, _

class ResUsers(models.Model):
    _inherit = 'res.users'

    sh_is_allow_z_report = fields.Boolean(string="Allow to Generate Z-Report ?")

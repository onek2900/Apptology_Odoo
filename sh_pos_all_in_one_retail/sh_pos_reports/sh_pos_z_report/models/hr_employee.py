# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from odoo import models, fields


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    sh_is_allow_z_report = fields.Boolean(
        string="Allow to Generate Z-Report ?")
    
class HrEmplloyeePublicInherit(models.Model):
    _inherit = "hr.employee.public"

    sh_is_allow_z_report = fields.Boolean(
        string="Allow to Generate Z-Report ?")

# Part of Softhealer Technologies.
from odoo import fields, models

class SHResUsers(models.Model):
    _inherit = "res.users"

    sign = fields.Text(string='Signature')

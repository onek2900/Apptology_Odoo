# Part of Softhealer Technologies.
from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    enable_whatsapp = fields.Boolean(string="Enable Whatsapp")

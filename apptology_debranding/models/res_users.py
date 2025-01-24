from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    odoobot_state = fields.Selection(string="ApptologyBot Status")
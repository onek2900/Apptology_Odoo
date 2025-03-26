from odoo import models, fields

class Currency(models.Model):
    _inherit = 'res.currency'

    symbol = fields.Char(string='Currency Symbol', default='﷼')

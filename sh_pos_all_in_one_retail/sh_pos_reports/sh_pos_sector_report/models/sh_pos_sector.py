# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from odoo import models, fields


class Sector(models.Model):
    _name = 'sh.pos.sector'
    _description = "POS Sector"
    _order = 'sequence, id'

    name = fields.Char(string="Name", required=True)
    from_time = fields.Float(string="From", required=True)
    to_time = fields.Float(string="To", required=True)
    sequence = fields.Integer("Sequence")

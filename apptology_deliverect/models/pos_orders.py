# -*- coding: utf-8 -*-
from email.policy import default

from odoo import api, fields, models



class PosOrder(models.Model):
    """Inheriting the pos order model"""
    _inherit = "pos.order"

    order_type = fields.Selection([
        ('1', 'Pick up'),
        ('2', 'Delivery'),
        ('3', 'Eat In'),
        ('4', 'Curbside')
    ], string='Order Type', default='1')

# coding: utf-8

from odoo import fields, models


class ShToppingGroup(models.Model):
    _inherit = 'sh.topping.group'

    min = fields.Integer(string="Min")
    max=fields.Integer(string="Max")
    multi_max=fields.Integer(string="Multi Max")
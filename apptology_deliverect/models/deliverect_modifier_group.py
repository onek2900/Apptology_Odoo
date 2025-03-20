# -*- coding: utf-8 -*-
from odoo import models, fields


class DeliverectModifierGroup(models.Model):
    """Class for Deliverect Modifier Groups"""
    _name = "deliverect.modifier.group"

    name = fields.Char(string="Name",help="Name of the modifier group")
    description = fields.Text(string="Description",help="Description for the modifier group")
    modifier_product_lines_ids = fields.One2many("deliverect.modifier.product.lines", "modifier_group_id",
                                                 string="Modifier Product Lines")

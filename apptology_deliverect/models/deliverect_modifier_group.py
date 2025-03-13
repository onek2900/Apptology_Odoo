# -*- coding: utf-8 -*-
import logging
from odoo import models, fields

_logger = logging.getLogger(__name__)


class DeliverectModifierGroup(models.Model):
    """Class for Modifier Groups"""
    _name = "deliverect.modifier.group"

    name = fields.Char(string="Name")
    description = fields.Text(string="Description")
    modifier_product_lines_ids = fields.One2many("deliverect.modifier.product.lines", "modifier_group_id",
                                                 string="Modifier Product Lines")


class DeliverectModifierProductLines(models.Model):
    """Class for Modifier Product Lines"""
    _name = "deliverect.modifier.product.lines"

    product_id = fields.Many2one(
        "product.product",
        domain=[('is_modifier', '=', True)],
        string="Modifier Product"
    )
    cost = fields.Float(string="Cost", related="product_id.lst_price")
    modifier_group_id = fields.Many2one("deliverect.modifier.group")

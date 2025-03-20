# -*- coding: utf-8 -*-
from odoo import models, fields


class ProductProduct(models.Model):
    """Inherit product.product to add custom fields."""
    _inherit = "product.product"

    channel_ids = fields.Many2many('deliverect.channel', string="Deliverect Channels",help="Deliverect Channels "
                                                                                           "available")
    delivery_tax = fields.Float(string="Delivery Tax",help="Delivery Tax for the product")
    takeaway_tax = fields.Float(string="Takeaway Tax",help="Takeaway Tax for the product")
    eat_in_tax = fields.Float(string="Eat-in Tax",help="Eat-in Tax for the product")
    allergens_and_tag_ids = fields.Many2many('deliverect.allergens', string="Allergens and Tags",help="Allergens and Tags for the product")
    product_note = fields.Text(string="Product Note",help="Deliverect Note for the product")
    modifier_group_ids = fields.Many2many('deliverect.modifier.group', string="Modifier Groups",help="Modifier "
                                                                                                      "Groups for the product")
    is_modifier = fields.Boolean(string="Is Modifier",help="Is Modifier for the product",default=False)

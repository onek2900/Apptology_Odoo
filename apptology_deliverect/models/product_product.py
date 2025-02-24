# -*- coding: utf-8 -*-
from email.policy import default

from odoo import models, fields
import logging
import requests
import base64

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = "product.product"

    product_type = fields.Selection(
        selection=[('1', 'Product'), ('2', 'Modifier'), ('3', 'Modifier Group'), ('4', 'Bundle')],default='1')
    all_channel_visible = fields.Boolean(string="All Channels Visible",default=True)
    hide_channel_ids = fields.Many2many('deliverect.channel', string="Hide Channels")
    delivery_tax = fields.Float(string="Delivery Tax")
    takeaway_tax = fields.Float(string="Takeaway Tax")
    eat_in_tax = fields.Float(string="Eat-in Tax")
    allergens_and_tag_ids = fields.Many2many('deliverect.allergens', string="Allergens and Tags")


# -*- coding: utf-8 -*-
import logging
from odoo import models, fields

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    """Inherited Product Template to add custom fields."""
    _inherit = "product.template"

    product_type = fields.Selection(
        selection=[('1', 'Product'), ('2', 'Modifier'), ('3', 'Modifier Group'), ('4', 'Bundle')], default='1')
    all_channel_visible = fields.Boolean(string="All Channels Visible", default=True)
    hide_channel_ids = fields.Many2many('deliverect.channel', string="Hide Channels")
    delivery_tax = fields.Float(string="Delivery Tax")
    takeaway_tax = fields.Float(string="Takeaway Tax")
    eat_in_tax = fields.Float(string="Eat-in Tax")
    allergens_and_tag_ids = fields.Many2many('deliverect.allergens', string="Allergens and Tags")

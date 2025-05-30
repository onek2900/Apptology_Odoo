# -*- coding: utf-8 -*-
from odoo import models, fields


class ProductTemplate(models.Model):
    """Inherit product.template to add custom fields."""
    _inherit = "product.template"

    deliverect_variant_note = fields.Char(string="Variant Note", help="Description for the variants")
    allergens_and_tag_ids = fields.Many2many('deliverect.allergens', string="Allergens and Tags",help="Allergens and Tags for the product")
    deliverect_variant_description=fields.Text(string="Variant Description", help="Description for the variants")
  

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

    def action_sync_product(self):
        """Sync products and categories with Deliverect API"""
        url = "https://api.staging.deliverect.com/productAndCategories"
        token = self.env['deliverect.api'].sudo().generate_auth_token()
        product_data = self.create_product_data()
        config_parameter = self.env['ir.config_parameter'].sudo()
        account_id = config_parameter.get_param('account_id')
        location_id = config_parameter.get_param('location_id')

        payload = {
            "priceLevels": [],
            "categories": product_data.get('categories'),
            "products": product_data.get('products'),
            "accountId": account_id,
            "locationId": location_id
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {token}"
        }
        response = requests.post(url, json=payload, headers=headers)
        _logger.info(f"Product sync response: {response.status_code} - {response.text}")


    def create_product_data(self):
        """Prepare product data for syncing"""
        products_to_sync = self.env['product.product'].sudo().search(
            [('active', '=', True), ('available_in_pos', '=', True)], limit=5)
        pos_categories = self.env['pos.category'].sudo().search([]).mapped(lambda p: {
            "name": p.name,
            "posCategoryId": p.id
        })
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        product_data = products_to_sync.mapped(lambda product: {
            "name": product.name,
            "isCombo":product.detailed_type == 'combo',
            "plu": product.default_code,
            "price": int(product.lst_price*100),
            "deliveryTax": product.taxes_id.amount*1000,
            "takeawayTax": product.taxes_id.amount*1000,
            "eatInTax": product.taxes_id.amount*1000,
            "visible": product.all_channel_visible,
            "posCategoryIds": [str(cat.id) for cat in product.pos_categ_ids] if product.pos_categ_ids else [],
            "imageUrl": f"{base_url}/web/image/product.product/{product.id}/image_128",
            "productTags": [allergen.allergen_id for allergen in product.allergens_and_tag_ids] if
            product.allergens_and_tag_ids else [],

        })
        return {
            'categories': pos_categories,
            'products': product_data
        }

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

    def create_combo_product_data(self, combo_product):
        deliverect_products = []

        # Convert main combo product (Type 1)
        main_product = {
            "productType": 1,
            "isCombo": True,
            "plu": f"P-{combo_product.id}",
            "price": 0,
            "name": combo_product.name,
            "imageUrl": self.image_upload(combo_product.product_tmpl_id.id),
            "subProducts": []
        }
        # Process combo attributes (Type 3 - modifier groups)
        sum_base_price = sum(combo_product.combo_ids.mapped('base_price'))
        for combo in combo_product.combo_ids:
            modifier_group_plu = f"CC-{combo.id}"
            main_product["subProducts"].append(modifier_group_plu)
            modifier_group = {
                "productType": 3,
                "plu": modifier_group_plu,
                "name": combo.name,
                "subProducts": [],
            }
            base_price = combo.base_price

            # Process combo lines (Type 2 - modifiers)
            for line in combo.combo_line_ids:
                product = line.product_id
                product_tax = self.env['product.product'].sudo().browse(product.id).taxes_id.amount
                modifier_plu = f"PM-{product.id}"
                modifier_group["subProducts"].append(modifier_plu)
                modifier = {
                    "productType": 2,
                    "plu": modifier_plu,
                    "price": round((((base_price / sum_base_price) * combo_product.lst_price) + line.combo_price),2
                                   ) * 100,
                    "name": product.name,
                    "imageUrl": self.image_upload(product.product_tmpl_id.id),
                    "deliveryTax": product_tax*1000,
                    "takeawayTax": product_tax*1000,
                    "eatInTax": product_tax*1000,
                }
                deliverect_products.append(modifier)
            deliverect_products.append(modifier_group)
        deliverect_products.insert(0, main_product)
        return deliverect_products

    def action_sync_product(self):
        """Sync products and categories with Deliverect API"""
        url = "https://api.staging.deliverect.com/productAndCategories"
        token = self.env['deliverect.api'].sudo().generate_auth_token()
        config_parameter = self.env['ir.config_parameter'].sudo()
        account_id = config_parameter.get_param('account_id')
        location_id = config_parameter.get_param('location_id')
        product_data = self.create_product_data()
        combo_products = self.env['product.product'].sudo().search([('detailed_type', '=', 'combo')])
        for combo in combo_products:
            product_data += self.create_combo_product_data(combo)
        pos_categories = self.env['pos.category'].sudo().search([]).mapped(
            lambda category: {
                "name": category.name,
                "posCategoryId": category.id,
            })
        payload = {
            "priceLevels": [],
            "categories":pos_categories,
            "products": product_data,
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

    def image_upload(self, product_tmpl_id):
        model = 'product.template'
        image = 'image_1920'
        attachment_id = self.env['ir.attachment'].sudo().search(
            domain=[('res_model', '=', model),
                    ('res_id', '=', product_tmpl_id),
                    ('res_field', '=', image)]
        )
        product_image_url = False
        if attachment_id:
            attachment_id.write({'public': True})
            base_url = self.env['ir.config_parameter'].sudo().get_param(
                'web.base.url')
            product_image_url = f"{base_url}{attachment_id.image_src}.jpg"
        return product_image_url

    def create_product_data(self):
        products = self.env['product.product'].sudo().search([('active', '=', True),
                                                                 ('detailed_type', '!=', 'combo'),
                                                                 ('attribute_line_ids', '=', False),
                                                                 ('available_in_pos', '=', True)])
        return products.mapped(lambda product: {
            "name": product.name,
            "plu": f"P-{product.id}",
            "price": int(product.lst_price * 100),
            "productType": 1,
            "deliveryTax": product.taxes_id.amount * 1000,
            "takeawayTax": product.taxes_id.amount * 1000,
            "eatInTax": product.taxes_id.amount * 1000,
            "imageUrl": self.image_upload(product.product_tmpl_id.id),
        })
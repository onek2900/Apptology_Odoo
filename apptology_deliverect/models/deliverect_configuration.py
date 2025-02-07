# -*- coding: utf-8 -*-

import requests
from odoo import models, fields
from odoo.http import request


class DeliverectConfiguration(models.Model):
    """ the deliverect configuration model"""
    _name = "deliverect.configuration"

    name = fields.Char(string="Name")
    client_id = fields.Char(string="Client ID")
    client_secret = fields.Char(string="Client Secret")
    account_id=fields.Char(string="Account ID")
    location_id=fields.Char(string="Location ID")

    def action_sync_product(self):
        url = "https://api.staging.deliverect.com/productAndCategories"
        token=self.generate_auth_token()
        product_data = self.create_product_data()
        payload = {
            "priceLevels": [],
            "categories": product_data.get('categories'),
            "products": product_data.get('products'),
            "accountId": "67a075460cfd6d82d1f09e30",
            "locationId": "67a075480cfd6d82d1f09e35"
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {token}"
        }
        response = requests.post(url, json=payload, headers=headers)

    def generate_auth_token(self):
        """Generate Deliverect API access token."""
        url = "https://api.staging.deliverect.com/oauth/token"

        payload = {
            "audience": "https://api.staging.deliverect.com",
            "grant_type": "token",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json"
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            return response.json().get('access_token')
        except requests.exceptions.RequestException as e:
            _logger.error(f"Failed to generate Deliverect token: {str(e)}")
            return None

    def create_product_data(self):
        products_to_sync = request.env['product.product'].sudo().search(
            [('active', '=', True), ('available_in_pos', '=', True)],limit=15)
        pos_categories= request.env['pos.category'].sudo().search([]).mapped(lambda p:{
            "name":p.name,
            "posCategoryId":p.id
        })
        print(pos_categories)
        product_data = products_to_sync.mapped(lambda p: {
            "name": p.name,
            "plu": p.default_code or f'SKU-{p.id}',
            "price": p.list_price,
            "deliveryTax": 11
        })
        print(product_data)
        return {
            'categories': pos_categories,
            'products': product_data
        }

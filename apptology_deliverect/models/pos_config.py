# -*- coding: utf-8 -*-
import logging
import requests
from odoo import fields, models

_logger = logging.getLogger(__name__)


class PosConfig(models.Model):
    """Inherited class to add new fields to pos.config"""
    _inherit = 'pos.config'

    auto_approve = fields.Boolean(string="Auto Approve", help="Automatically approve all orders from Deliverect")
    client_id = fields.Char(string="Client ID",help="Client ID provided by Deliverect")
    client_secret = fields.Char(string="Client Secret",help="Client Secret provided by Deliverect")
    account_id = fields.Char(string="Account ID",help="Account ID provided by Deliverect")
    location_id = fields.Char(string="Location ID",help='Location ID provided by Deliverect')
    status_message = fields.Char(string="Registration Status Message",help="Registration Status Message")
    order_status_message = fields.Char(string="Order Status Message",help="Order Status Message")

    def toggle_approve(self):
        """function to toggle approve button"""
        if self.auto_approve:
            self.auto_approve = False
        else:
            self.auto_approve = True

    def force_sync_pos(self):
        """function to force sync products from Deliverect"""
        force_sync = self.action_sync_product()
        if force_sync:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Success',
                    'message': f'Force Sync Complete',
                    'sticky': False,
                    'type': 'success',
                }
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Failure',
                    'message': f'Error Encountered while Force Syncing',
                    'sticky': False,
                    'type': 'danger',
                }
            }

    def show_deliverect_urls(self):
        """function to show deliverect related data in wizard"""
        deliverect_payment_method = self.env.ref("apptology_deliverect.pos_payment_method_deliverect")
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        registration_url = f"{base_url}/deliverect/pos/register/{self.id}"
        orders_url = f"{base_url}/deliverect/pos/orders/{self.id}"
        products_url = f"{base_url}/deliverect/pos/products/{self.id}"
        order_status_message = ""
        if deliverect_payment_method.id not in self.payment_method_ids.ids:
            order_status_message += "Unable to Accept Order - Deliverect Payment Method not selected"
        elif not self.current_session_id:
            order_status_message += "Unable to Accept Orders - Inactive Session"
        return {
            'name': 'Deliverect URLs',
            'type': 'ir.actions.act_window',
            'res_model': 'deliverect.info.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_registration_url': registration_url,
                'default_orders_url': orders_url,
                'default_products_url': products_url,
                'default_location_id': self.location_id,
                'default_status_message': self.status_message if self.status_message else "POS Not Registered",
                'default_order_status_message': order_status_message if order_status_message else "POS Ready To Accept "
                                                                                                  "Orders"
            },
            'flags': {'mode': 'readonly'},
        }

    def update_allergens(self):
        """function to update allergens"""
        allergens_updated = self.env['deliverect.allergens'].sudo().update_allergens()
        if allergens_updated:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Success',
                    'message': "Allergens Updated Successfully",
                    'type': 'success',
                }
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Failure',
                    'message': "Error Updating Allergens",
                    'type': 'danger',
                }
            }
    def create_customers_channel(self):
        """function for creating channel customers"""
        self.env['deliverect.channel'].sudo().update_channel()
        token = self.env['deliverect.api'].sudo().generate_auth_token()
        if not token:
            _logger.error("No authentication token received. Aborting channel update.")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Failure',
                    'message': "Error Generating Authentication Token",
                    'type': 'danger',
                }
            }
        location_id = self.location_id
        embedded_param = '{"channelLinks":1}'
        url = f'https://api.staging.deliverect.com/locations/{location_id}?embedded={embedded_param}'
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {token}"
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            account_data = response.json()
            channel = [channel["channel"] for channel in account_data.get("channelLinks", [])]
            channel_records = self.env['deliverect.channel'].sudo().search([('channel_id', 'in', channel)])
            created_partner_ids = []
            for channel_record in channel_records:
                existing_partner = self.env['res.partner'].sudo().search(
                    [('channel_id', '=', channel_record.channel_id)],
                    limit=1)
                if not existing_partner:
                    new_partner = self.env['res.partner'].sudo().create({
                        'name': channel_record.name,
                        'channel_id': channel_record.channel_id,
                    })
                    created_partner_ids.append(new_partner.id)
                    _logger.info(f"Created new partner: {new_partner.name} with Channel ID: {new_partner.channel_id}")
                else:
                    _logger.info(
                        f"Partner already exists for Channel ID {existing_partner.channel_id}: {existing_partner.name}")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Success',
                    'message': f"Created Partners "
                               f"{','.join(map(str, created_partner_ids))}" if created_partner_ids else f"No New "
                                                                                                        f"partners "
                                                                                                        f"Found",
                    'type': 'success',
                }
            }

        except requests.exceptions.RequestException as e:
            _logger.error(f"Failed to create partners for the location: {str(e)}")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Failure',
                    'message': "Error Encountered while creating partners",
                    'type': 'danger',
                }
            }

    def create_combo_product_data(self, combo_product):
        """function to create combo product data for Deliverect"""
        deliverect_products = []

        main_product = {
            "productType": 1,
            "isCombo": True,
            "plu": f"P-{combo_product.id}",
            "price": 0,
            "name": combo_product.name,
            "imageUrl": self.image_upload(combo_product.product_tmpl_id.id),
            "subProducts": [],
            "productTags": [allergen.allergen_id for allergen in
                            combo_product.allergens_and_tag_ids] if combo_product.allergens_and_tag_ids else []
        }
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

            for line in combo.combo_line_ids:
                product = line.product_id
                product_tax = self.env['product.product'].sudo().browse(product.id).taxes_id.amount
                modifier_plu = f"PM-{product.id}"
                modifier_group["subProducts"].append(modifier_plu)
                modifier = {
                    "productType": 2,
                    "plu": modifier_plu,
                    "price": round((((base_price / sum_base_price) * combo_product.lst_price) + line.combo_price), 2
                                   ) * 100,
                    "name": product.name,
                    "imageUrl": self.image_upload(product.product_tmpl_id.id),
                    "deliveryTax": product_tax * 1000,
                    "takeawayTax": product_tax * 1000,
                    "eatInTax": product_tax * 1000,
                }
                deliverect_products.append(modifier)
            deliverect_products.append(modifier_group)
        deliverect_products.insert(0, main_product)
        return deliverect_products

    def action_sync_product(self):
        """Sync products and categories with Deliverect API"""
        try:
            url = "https://api.staging.deliverect.com/productAndCategories"
            token = self.env['deliverect.api'].sudo().generate_auth_token()
            account_id = self.account_id
            location_id = self.location_id
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
                "categories": pos_categories,
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
            if response.status_code == 200:
                return True
            else:
                return False
        except Exception as e:
            _logger.error(f"Product sync failed: {e}")
            return False

    def image_upload(self, product_tmpl_id):
        """function to upload product image to Deliverect"""
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
        """function to create product data for Deliverect"""
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
            "productTags": [allergen.allergen_id for allergen in
                            product.allergens_and_tag_ids] if product.allergens_and_tag_ids else []
        })

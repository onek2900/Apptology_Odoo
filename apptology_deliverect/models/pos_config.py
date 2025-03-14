# -*- coding: utf-8 -*-
import json
import logging
import requests
from odoo import fields, models, Command

_logger = logging.getLogger(__name__)


class PosConfig(models.Model):
    """Inherited class to add new fields to pos.config"""
    _inherit = 'pos.config'

    auto_approve = fields.Boolean(string="Auto Approve", help="Automatically approve all orders from Deliverect")
    client_id = fields.Char(string="Client ID", help="Client ID provided by Deliverect")
    client_secret = fields.Char(string="Client Secret", help="Client Secret provided by Deliverect")
    account_id = fields.Char(string="Account ID", help="Account ID provided by Deliverect")
    location_id = fields.Char(string="Location ID", help='Location ID provided by Deliverect')
    status_message = fields.Char(string="Registration Status Message", help="Registration Status Message")
    order_status_message = fields.Char(string="Order Status Message", help="Order Status Message")

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

    def create_combo_product_data(self):
        """function to create combo product data for Deliverect"""
        combo_products = self.env['product.product'].sudo().search([('detailed_type', '=', 'combo')], limit=1)
        combo_products_data = []
        for combo_product in combo_products:
            combo_data = []

            main_product = {
                "productType": 1,
                "isCombo": True,
                "plu": f"PROD-{combo_product.id}",
                "price": combo_product.lst_price * 100,
                "name": combo_product.name,
                "imageUrl": self.image_upload(combo_product.product_tmpl_id.id),
                "subProducts": [],
                "productTags": [allergen.allergen_id for allergen in
                                combo_product.allergens_and_tag_ids] if combo_product.allergens_and_tag_ids else []
            }
            sum_base_price = sum(combo_product.combo_ids.mapped('base_price'))
            for combo in combo_product.combo_ids:
                modifier_group_plu = f"MOD_GRP-{combo.id}"
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
                    modifier_plu = f"MOD-{product.id}"
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
                    combo_data.append(modifier)
                combo_data.append(modifier_group)
            combo_data.insert(0, main_product)
            combo_products_data += combo_data
        print(combo_products_data)
        return combo_products_data

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

    def create_product_with_modifier(self):
        """function to create product with modifier for Deliverect"""
        products = self.env['product.product'].sudo().search([('active', '=', True),
                                                              ('detailed_type', '!=', 'combo'),
                                                              ('modifier_group_ids', '!=', False),
                                                              ('pos_categ_ids', 'in',
                                                               self.iface_available_categ_ids.ids),
                                                              ('available_in_pos', '=', True)])
        print('product with modifier :', products)
        return products.mapped(lambda product: {
            "name": product.name,
            "plu": f"PRD-{product.id}",
            "price": int(product.lst_price * 100),
            "productType": 1,
            "deliveryTax": product.taxes_id.amount * 1000,
            "takeawayTax": product.taxes_id.amount * 1000,
            "eatInTax": product.taxes_id.amount * 1000,
            "description": product.product_note,
            "imageUrl": self.image_upload(product.product_tmpl_id.id),
            "subProducts": [
                f"MOD_GRP-{group.id}" for group in product.modifier_group_ids
            ]
        })

    def create_modifier_and_modifier_group(self):
        """function to sync modifiers with Deliverect"""
        modifiers = self.env['product.product'].sudo().search([('is_modifier', '=', True)])
        print('modifiers :', modifiers)
        modifier_groups = self.env['deliverect.modifier.group'].sudo().search([])
        print('modifier groups :', modifier_groups)

        modifiers_data = modifiers.mapped(lambda modifier: {
            "name": modifier.name,
            "plu": f"MOD-{modifier.id}",
            "price": int(modifier.lst_price * 100),
            "productType": 2,
            "deliveryTax": modifier.taxes_id.amount * 1000,
            "takeawayTax": modifier.taxes_id.amount * 1000,
            "eatInTax": modifier.taxes_id.amount * 1000,
            "description": modifier.product_note,
            "imageUrl": self.image_upload(modifier.product_tmpl_id.id),
            "productTags": [allergen.allergen_id for allergen in
                            modifier.allergens_and_tag_ids] if modifier.allergens_and_tag_ids else []
        })
        modifier_group_data = modifier_groups.mapped(lambda group: {
            "productType": 3,
            "plu": f"MOD_GRP-{group.id}",
            "name": group.name,
            "description": group.description,
            "subProducts": [f"MOD-{modifier.product_id.id}" for modifier in group.modifier_product_lines_ids],
        })
        return modifiers_data + modifier_group_data

    def create_product_data(self):
        """function to create product data for Deliverect"""
        products = self.env['product.product'].sudo().search([('active', '=', True),
                                                              ('is_modifier', '=', False),
                                                              ('detailed_type', '!=', 'combo'),
                                                              ('modifier_group_ids', '=', False),
                                                              ('pos_categ_ids', 'in',
                                                               self.iface_available_categ_ids.ids),
                                                              ('available_in_pos', '=', True)])
        return products.mapped(lambda product: {
            "name": product.name,
            "plu": f"PRD-{product.id}",
            "price": int(product.lst_price * 100),
            "productType": 1,
            "deliveryTax": product.taxes_id.amount * 1000,
            "takeawayTax": product.taxes_id.amount * 1000,
            "eatInTax": product.taxes_id.amount * 1000,
            "description": product.product_note,
            "imageUrl": self.image_upload(product.product_tmpl_id.id),
            "productTags": [allergen.allergen_id for allergen in
                            product.allergens_and_tag_ids] if product.allergens_and_tag_ids else []
        })

    def create_variant_product_data(self):
        """function to create variant product data for Deliverect"""
        main_variant_products = self.env['product.template'].sudo().search([('active', '=', True),
                                                                            ('detailed_type', '!=', 'combo'),
                                                                            ('attribute_line_ids', '!=', False),
                                                                            ('pos_categ_ids', 'in',
                                                                             self.iface_available_categ_ids.ids),
                                                                            ('available_in_pos', '=', True)])
        main_product_data = main_variant_products.mapped(lambda product: {
            "productType": 1,
            "plu": f"VAR-{product.id}",
            "price": int(product.list_price * 100),
            "name": product.name,
            "imageUrl": self.image_upload(product.id),
            "description": "",
            "isVariant": True,
            "deliveryTax": product.taxes_id.amount * 1000,
            "takeawayTax": product.taxes_id.amount * 1000,
            "eatInTax": product.taxes_id.amount * 1000,
            "subProducts": [
                f"VAR_GRP-{product.id}"
            ]
        })
        main_product_group_data = main_variant_products.mapped(lambda product: {
            "productType": 3,
            "plu": f"VAR_GRP-{product.id}",
            "name": product.deliverect_variant_note,
            "description": product.deliverect_variant_description,
            "isVariantGroup": True,
            "subProducts": [f"PRD-{variant.id}" for variant in self.env['product.product'].search([('active', '=',
                                                                                                    True),
                                                                                                   (
                                                                                                       "product_tmpl_id",
                                                                                                       "=",
                                                                                                       product.id)])]
        })
        return main_product_group_data + main_product_data

    def clear_products(self):
        try:
            url = "https://api.staging.deliverect.com/productAndCategories"
            token = self.env['deliverect.api'].sudo().generate_auth_token()
            account_id = self.account_id
            location_id = self.location_id
            payload = {
                "priceLevels": [],
                "categories": [],
                "products": [
                    {
                        "productType": 1,
                        "plu": "VAR-1",
                        "price": 800,
                        "name": "3 Pieces",
                        "posProductId": "POS-003",
                        "imageUrl": "",
                        "description": "",
                        "deliveryTax": 9000,
                        "takeawayTax": 9000,
                        "eatInTax": 9000
                    },
                    {
                        "productType": 1,
                        "plu": "VAR-2",
                        "price": 1100,
                        "name": "6 Pieces",
                        "posProductId": "POS-004",
                        "imageUrl": "",
                        "description": "",
                        "deliveryTax": 9000,
                        "takeawayTax": 9000,
                        "eatInTax": 9000
                    },
                    {
                        "productType": 1,
                        "plu": "VAR-3",
                        "price": 1350,
                        "name": "9 Pieces",
                        "posProductId": "POS-005",
                        "imageUrl": "",
                        "description": "",
                        "deliveryTax": 9000,
                        "takeawayTax": 9000,
                        "eatInTax": 9000
                    },
                    {
                        "productType": 3,
                        "plu": "MG-VAR-1",
                        "name": "How many pieces?",
                        "posProductId": "POS-002",
                        "description": "",
                        "isVariantGroup": True,
                        "subProducts": [
                            "VAR-1",
                            "VAR-2",
                            "VAR-3"
                        ],
                        "min": 1,
                        "max": 1
                    },
                    {
                        "productType": 1,
                        "plu": "VAR-PROD-1",
                        "price": 0,
                        "name": "Chicken Tenders",
                        "posProductId": "POS-001",
                        "posCategoryIds": [
                            "CHK"
                        ],
                        "imageUrl": "https://storage.googleapis.com/ikona-bucket-staging/images/5ff6ee089328c8aefeeabe33/chicken-62285f90db5986001ebf58d5.jpg",
                        "description": "Choose 3, 6 or 9 Pieces of Delicious Fried Chicken",
                        "isVariant": True,
                        "deliveryTax": 9000,
                        "takeawayTax": 9000,
                        "eatInTax": 9000,
                        "subProducts": [
                            "MG-VAR-1"
                        ]
                    }
                ],
                "accountId": account_id,
                "locationId": location_id
            }
            headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "authorization": f"Bearer {token}"
            }
            response = requests.post(url, json=payload, headers=headers)
            _logger.info(f"Products clear response: {response.status_code} - {response.text}")
            if response.status_code == 200:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Success',
                        'message': f"Successfully cleared products",
                        'type': 'success',
                    }
                }
            else:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Failure',
                        'message': f"Failed to clear products",
                        'type': 'success',
                    }
                }

        except Exception as e:
            _logger.error(f"Product sync failed: {e}")
            return False

    def create_deliverect_product_data(self):
        product_data = []
        product_data += self.create_product_data()
        product_data += self.create_modifier_and_modifier_group()
        product_data += self.create_product_with_modifier()
        product_data += self.create_variant_product_data()
        # product_data += self.create_combo_product_data()
        print(product_data)
        return product_data

    def action_sync_product(self):
        """Sync products and categories with Deliverect API"""
        try:
            url = "https://api.staging.deliverect.com/productAndCategories"
            token = self.env['deliverect.api'].sudo().generate_auth_token()
            account_id = self.account_id
            location_id = self.location_id
            payload = {
                "priceLevels": [],
                "categories": [],
                "products": self.create_deliverect_product_data(),
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

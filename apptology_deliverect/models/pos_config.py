# -*- coding: utf-8 -*-
import logging
import requests
from odoo import fields, models

_logger = logging.getLogger(__name__)


class PosConfig(models.Model):
    """Inherit class to add new fields and function"""
    _inherit = 'pos.config'

    auto_approve = fields.Boolean(string="Auto Approve", help="Automatically approve all orders from Deliverect")
    account_id = fields.Char(string="Account ID", help="Account ID provided by Deliverect")
    pos_id = fields.Char(string="POS ID", help="POS ID Provided to deliverect for registration")
    location_id = fields.Char(string="Location ID", help='Location ID provided by Deliverect')
    internal_pos_id = fields.Char(string="POS ID", help='POS ID provided to Deliverect')
    status_message = fields.Char(string="Registration Status Message", help="Registration Status Message")
    order_status_message = fields.Char(string="Order Status Message", help="Order Status Message")

    def toggle_approve(self):
        """Toggle the approval button."""
        self.auto_approve = not self.auto_approve

    def force_sync_pos(self):
        """Force sync products from POS to Deliverect."""
        success = self.action_sync_product()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success' if success else 'Failure',
                'message': 'Force Sync Complete' if success else 'Error Encountered while Force Syncing',
                'sticky': False,
                'type': 'success' if success else 'danger',
            }
        }

    def show_deliverect_urls(self):
        """Show deliverect urls in a wizard"""
        deliverect_payment_method = self.env['pos.payment.method'].search([('company_id', '=', self.company_id.id),
                                                                           ('is_deliverect_payment_method', '=',
                                                                            True)],limit=1)
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
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
                'default_registration_url': f"{base_url}/deliverect/pos/register",
                'default_orders_url': f"{base_url}/deliverect/pos/orders/{self.pos_id}",
                'default_products_url': f"{base_url}/deliverect/pos/products/{self.pos_id}",
                'default_location_id': self.location_id,
                'default_internal_pos_id': self.pos_id,
                'default_status_message': self.status_message if self.status_message else "POS Not Registered",
                'default_order_status_message': order_status_message if order_status_message else "POS Ready To Accept "
                                                                                                  "Orders"
            },
            'flags': {'mode': 'readonly'},
        }

    def update_allergens(self):
        """Update allergens from Deliverect."""
        success = self.env['deliverect.allergens'].sudo().update_allergens()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success' if success else 'Failure',
                'message': "Allergens Updated Successfully" if success else "Error Updating Allergens",
                'type': 'success' if success else 'danger',
            }
        }

    def create_customers_channel(self):
        """Function for creating channel customers"""
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
        url = f'https://api.deliverect.com/locations/{location_id}?embedded={embedded_param}'
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

    def image_upload(self, product_tmpl_id):
        """Function to upload product image to deliverect."""
        attachment_id = self.env['ir.attachment'].sudo().search(
            domain=[('res_model', '=', 'product.template'),
                    ('res_id', '=', product_tmpl_id),
                    ('res_field', '=', 'image_1920')]
        )
        product_image_url = False
        if attachment_id:
            attachment_id.write({'public': True})
            base_url = self.env['ir.config_parameter'].sudo().get_param(
                'web.base.url')
            product_image_url = f"{base_url}{attachment_id.image_src}.jpg"
        return product_image_url

    def create_product_json(self, product_type, plu, product_price, product_name, product_arabicname, product_tmpl_id, product_note,
                            product_tax, product_category_ids):
        """Generate product JSON data for Deliverect."""
        if not product_arabicname:
            lang_code = self.env['res.lang'].search([('code', 'like', 'ar%')], limit=1).code or 'ar'
            product = self.env['product.product'].search([('product_tmpl_id','=',product_tmpl_id)])
            arabicname = product.with_context(lang=lang_code).name
            description_arabic = product.product_note_arabic or product.with_context(lang=lang_code).product_note
        return {
            "productType": product_type,
            "plu": plu,
            "price": product_price * 100,
            "name": product_name,
            "nameTranslations": {
               "en": product_name,
                "ar": product_arabicname or arabicname
                },
            "imageUrl": self.image_upload(product_tmpl_id),
            "description": product_note or "",
            "descriptionTranslations": {
                "ar": description_arabic,
                "en": product_note},
            "deliveryTax": product_tax * 1000,
            "takeawayTax": product_tax * 1000,
            "eatInTax": product_tax * 1000,
            "posCategoryIds": product_category_ids
        }

    def create_product_with_modifier(self):
        """create product with modifier in deliverect"""
        domain = [('active', '=', True),
                  ('detailed_type', '!=', 'combo'),
                  ('modifier_group_ids', '!=', False),
                  ('available_in_pos', '=', True)]
        if self.iface_available_categ_ids:
            domain.append(('pos_categ_ids', 'in',
                           self.iface_available_categ_ids.ids))
        products = self.env['product.product'].sudo().search(domain)
        return products.mapped(lambda prod: {
            **self.create_product_json(1, f"PRD-{prod.id}", prod.lst_price, prod.name, prod.product_arabicname, prod.product_tmpl_id.id,
                                       prod.product_note, prod.taxes_id[0].amount if prod.taxes_id else 0.0,
                                       prod.pos_categ_ids.ids),
            "subProducts": [f"MOD_GRP-{group.id}" for group in prod.modifier_group_ids]
        })

    def create_modifier_and_modifier_group(self):
        """create modifier and modifier group in deliverect"""
        modifiers = self.env['product.product'].sudo().search([('is_modifier', '=', True)])
        modifier_groups = self.env['deliverect.modifier.group'].sudo().search([])
        modifiers_data = modifiers.mapped(lambda prod: {
            **self.create_product_json(2, f"MOD-{prod.id}", prod.lst_price, prod.name, prod.product_arabicname, prod.product_tmpl_id.id,
                                       prod.product_note, prod.taxes_id[0].amount if prod.taxes_id else 0.0,
                                       prod.pos_categ_ids.ids),
            "productTags": [allergen.allergen_id for allergen in
                            prod.allergens_and_tag_ids] if prod.allergens_and_tag_ids else []
        })
        modifier_group_data = modifier_groups.mapped(lambda group: {
            "productType": 3,
            "plu": f"MOD_GRP-{group.id}",
            "name": group.name,
            "description": group.description,
            "subProducts": [f"MOD-{modifier.product_id.id}" for modifier in group.modifier_product_lines_ids],
        })
        return modifiers_data + modifier_group_data

    def create_product_category_data(self):
        """create product category data for deliverect"""
        return [
            {'name': product_category['name'], 'posCategoryId': product_category['id']}
            for product_category in self.env['pos.category'].search_read([], ['id', 'name'])
        ]

    def create_product_data(self):
        """create normal products in deliverect"""
        domain = [('active', '=', True),
                  ('is_modifier', '=', False),
                  ('detailed_type', '!=', 'combo'),
                  ('modifier_group_ids', '=', False),
                  ('available_in_pos', '=', True)]
        if self.iface_available_categ_ids:
            domain.append(('pos_categ_ids', 'in',
                           self.iface_available_categ_ids.ids))
        products = self.env['product.product'].sudo().search(domain)
        return products.mapped(lambda prod: {
            **self.create_product_json(1, f"PRD-{prod.id}", prod.lst_price, prod.name, prod.product_arabicname, prod.product_tmpl_id.id,
                                       prod.product_note, prod.taxes_id[0].amount if
                                       prod.taxes_id else 0.0, prod.pos_categ_ids.ids),
            "productTags": [allergen.allergen_id for allergen in
                            prod.allergens_and_tag_ids] if prod.allergens_and_tag_ids else []
        })

    def create_deliverect_product_data(self):
        """function to create product data for deliverect"""
        product_data = []
        product_data += self.create_product_data()
        product_data += self.create_modifier_and_modifier_group()
        product_data += self.create_product_with_modifier()
        return product_data

    def action_sync_product(self):
        """function to sync products with deliverect"""
        try:
            url = "https://api.deliverect.com/productAndCategories"
            token = self.env['deliverect.api'].sudo().generate_auth_token()
            account_id = self.account_id
            location_id = self.location_id
            payload = {
                "priceLevels": [],
                "categories": self.create_product_category_data(),
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

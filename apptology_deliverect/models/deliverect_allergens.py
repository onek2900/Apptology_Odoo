# -*- coding: utf-8 -*-

import requests
from odoo import models, fields, api,_
import logging

_logger = logging.getLogger(__name__)


class DeliverectAllergens(models.Model):
    _name = "deliverect.allergens"
    _description = "Deliverect Allergens"

    name = fields.Char(string="Allergen", required=True)
    allergen_id = fields.Integer(string="Allergen ID", required=True, unique=True)

    def update_allergens(self):
        """Fetch and update Deliverect allergens"""
        url = "https://api.staging.deliverect.com/allAllergens"
        token = self.env["deliverect.api"].sudo().generate_auth_token()
        headers = {"accept": "application/json",
                   "authorization": f"Bearer {token}"}
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            allergens = response.json()

            for allergen in allergens:
                vals = {
                    "name": allergen.get("name"),
                    "allergen_id": allergen.get("allergenId"),
                }
                existing_allergen = self.env["deliverect.allergens"].search(
                    [("allergen_id", "=", allergen.get("allergenId"))], limit=1
                )
                if existing_allergen:
                    existing_allergen.write(vals)
                else:
                    self.env["deliverect.allergens"].create(vals)
            _logger.info("Allergen update successful.")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'success',
                    'message': _('Allergens updated successfully'),
                    'next': {'type': 'ir.actions.act_window_close'},
                }
            }

        except requests.exceptions.RequestException as e:
            _logger.error(f"Failed to fetch allergens from Deliverect: {str(e)}")

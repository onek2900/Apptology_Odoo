# -*- coding: utf-8 -*-

import requests
from odoo import models
import logging

_logger = logging.getLogger(__name__)

class DeliverectAPI(models.AbstractModel):
    _name = "deliverect.api"
    _description = "Deliverect API Helper"

    def generate_auth_token(self):
        url = "https://api.staging.deliverect.com/oauth/token"
        config_parameter = self.env['ir.config_parameter'].sudo()
        client_id = config_parameter.get_param('client_id')
        client_secret = config_parameter.get_param('client_secret')

        payload = {
            "audience": "https://api.staging.deliverect.com",
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json"
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json().get('access_token')
        except requests.exceptions.RequestException as e:
            _logger.error(f"Failed to generate Deliverect token: {str(e)}")
            return None

# -*- coding: utf-8 -*-
import logging
import requests
from odoo import models

_logger = logging.getLogger(__name__)

CLIENT_ID  = "nfFvT81dgv0EEVXc"
CLIENT_SECRET = "Q4wx5sqiElVgP4IIPcEUY5zJAljXi9Sy"

class DeliverectAPI(models.AbstractModel):
    """Class for Deliverect API Helper"""
    _name = "deliverect.api"
    _description = "Deliverect API Helper"

    def generate_auth_token(self):
        """Function for generating Deliverect authentication token"""
        url = "https://api.staging.deliverect.com/oauth/token"
        payload = {
            "audience": "https://api.staging.deliverect.com",
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET
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

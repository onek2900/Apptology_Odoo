# -*- coding: utf-8 -*-
import json

import requests
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class DeliverectChannel(models.Model):
    _name = "deliverect.channel"

    name = fields.Char(string="Name")
    channel_id = fields.Integer(string="Channel ID")

    def update_channel(self):
        print('update channel')
        token = self.env['deliverect.api'].sudo().generate_auth_token()
        if not token:
            _logger.error("No authentication token received. Aborting channel update.")
            return False

        # The JSON in the query parameter needs to be properly formatted and URL encoded
        where_clause = json.dumps({"account": "67a075460cfd6d82d1f09e30"})
        url = f'https://api.staging.deliverect.com/locations?sort=-_created&max_results=500&cursor=new&where={where_clause}'

        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {token}"
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            account_data = response.json()

            for rec in account_data.get('_items', []):
                channel_details = rec.get('channelLinksDetails', {})

                for channel_id, channel in channel_details.items():  # Extracting keys as channel_id
                    name = channel.get('name', 'Unknown Partner')

                    # Check if a partner already exists with this channel_id
                    existing_partner = self.env['res.partner'].sudo().search([('channel_id', '=', channel_id)], limit=1)

                    if not existing_partner:
                        # Create new partner
                        self.env['res.partner'].sudo().create({
                            'name': name,
                            'channel_id': channel_id,
                        })
                        _logger.info(f"Created new partner: {name} with Channel ID: {channel_id}")
                    else:
                        _logger.info(f"Partner already exists for Channel ID {channel_id}: {existing_partner.name}")
            return True

        except requests.exceptions.RequestException as e:
            _logger.error(f"Failed to fetch locations from Deliverect: {str(e)}")
            return False

    # def update_channel(self):
    #     """Fetch and update Deliverect channels"""
    #     token = self.env['deliverect.api'].sudo().generate_auth_token()
    #     if not token:
    #         _logger.error("No authentication token received. Aborting channel update.")
    #         return
    #
    #     url = "https://api.staging.deliverect.com/allChannels"
    #     headers = {
    #         "accept": "application/json",
    #         "authorization": f"Bearer {token}"
    #     }
    #     try:
    #         response = requests.get(url, headers=headers)
    #         response.raise_for_status()
    #         channels = response.json()
    #         for channel in channels:
    #             vals = {"name": channel.get("name")}
    #             self.env["deliverect.channel"].update_or_create_channel(channel.get("channelId"), vals)
    #     except requests.exceptions.RequestException as e:
    #         _logger.error(f"Failed to fetch data from Deliverect: {str(e)}")
    #
    # @api.model
    # def update_or_create_channel(self, channel_id, vals):
    #     """Create or update a channel record"""
    #     channel = self.search([('channel_id', '=', channel_id)], limit=1)
    #     if channel:
    #         channel.write(vals)
    #     else:
    #         vals["channel_id"] = channel_id
    #         self.create(vals)

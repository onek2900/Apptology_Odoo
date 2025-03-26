# -*- coding: utf-8 -*-
import json
import logging
import requests
from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class DeliverectChannel(models.Model):
    """Class for Deliverect channels"""
    _name = "deliverect.channel"

    name = fields.Char(string="Name",help="Name of the Deliverect channel")
    channel_id = fields.Integer(string="Channel ID",help="ID of the Deliverect channel")


    def update_channel(self):
        """Fetch and update Deliverect channels"""
        token = self.env['deliverect.api'].sudo().generate_auth_token()
        if not token:
            _logger.error("No authentication token received. Aborting channel update.")
            return

        url = "https://api.deliverect.com/allChannels"
        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {token}"
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            channels = response.json()
            for channel in channels:
                vals = {"name": channel.get("name")}
                self.env["deliverect.channel"].update_or_create_channel(channel.get("channelId"), vals)
        except requests.exceptions.RequestException as e:
            _logger.error(f"Failed to fetch data from Deliverect: {str(e)}")

    @api.model
    def update_or_create_channel(self, channel_id, vals):
        """Create or update a channel record"""
        channel = self.search([('channel_id', '=', channel_id)], limit=1)
        if channel:
            channel.write(vals)
        else:
            vals["channel_id"] = channel_id
            self.create(vals)

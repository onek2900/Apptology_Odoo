# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    apptology_google_places_autocomplete_enabled = fields.Boolean(
        string='Enable Google Places Autocomplete (POS)',
        config_parameter='apptology_address_autofill.google_places_enabled',
        help='Enable address autocomplete in POS customer editor using Google Places.'
    )
    apptology_google_places_api_key = fields.Char(
        string='Google Places API Key',
        config_parameter='apptology_address_autofill.google_places_api_key',
        help='Browser key with Places API enabled.'
    )


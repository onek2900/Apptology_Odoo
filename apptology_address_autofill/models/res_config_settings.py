from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    google_places_api_key = fields.Char(
        string="Google Places API Key",
        config_parameter="apptology_address_autofill.google_places_api_key",
        help="API key used to load Google Places Autocomplete in the backend.",
    )

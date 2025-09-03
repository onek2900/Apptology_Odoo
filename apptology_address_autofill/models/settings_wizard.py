from odoo import api, fields, models


class ApptologyAddressSettings(models.TransientModel):
    _name = "apptology.address.settings"
    _description = "Apptology Address Autofill Settings"

    google_places_api_key = fields.Char(string="Google Places API Key")

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if "google_places_api_key" in fields_list:
            param_key = "apptology_address_autofill.google_places_api_key"
            res["google_places_api_key"] = (
                self.env["ir.config_parameter"].sudo().get_param(param_key, default="")
            )
        return res

    def action_save(self):
        self.ensure_one()
        param_key = "apptology_address_autofill.google_places_api_key"
        self.env["ir.config_parameter"].sudo().set_param(
            param_key, self.google_places_api_key or ""
        )
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Settings Saved",
                "message": "Google Places API key updated.",
                "sticky": False,
                "type": "success",
            },
        }


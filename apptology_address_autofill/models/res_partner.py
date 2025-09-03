from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    gmap_autocomplete = fields.Char(
        string="Address Search",
        help=(
            "Type an address to search via Google Places. "
            "Selecting a suggestion will fill the address fields."
        ),
    )

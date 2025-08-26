from odoo import api, fields, models

import logging

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    module_apptology_pos_moneris = fields.Boolean(
        string="Moneris Payment Terminal",
        help="The transactions are processed by Moneris.",
    )

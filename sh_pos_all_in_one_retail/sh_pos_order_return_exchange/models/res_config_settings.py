# Part of Softhealer Technologies.

from odoo import models, fields, api


class ResConfigSettiongsInhert(models.TransientModel):
    _inherit = "res.config.settings"

    sh_allow_return = fields.Boolean(
        related="pos_config_id.sh_allow_return", readonly=False)
    sh_return_more_qty = fields.Boolean(
        related="pos_config_id.sh_return_more_qty", readonly=False)
    sh_return_print_receipt = fields.Boolean(
        related="pos_config_id.sh_return_print_receipt", readonly=False)
    sh_allow_exchange = fields.Boolean(
        related="pos_config_id.sh_allow_exchange", readonly=False)
    sh_exchange_print_receipt = fields.Boolean(
        related="pos_config_id.sh_exchange_print_receipt", readonly=False)

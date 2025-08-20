# Part of Softhealer Technologies.
# Copyright (C) Softhealer Technologies.

from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_sh_enable_default_customer = fields.Boolean(
        related="pos_config_id.sh_enable_default_customer", string="Enable POS Default Customer", readonly=False)
    pos_sh_default_customer_id = fields.Many2one(
        related="pos_config_id.sh_default_customer_id", string="Default Customer", readonly=False)

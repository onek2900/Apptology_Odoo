# Copyright (C) Softhealer Technologies.
# Part of Softhealer Technologies.

from odoo import models, fields

class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    pos_sh_pos_enable_customer_max_discount = fields.Boolean(related='pos_config_id.sh_pos_enable_customer_max_discount',
        string='Enable Customer Maximum Discount',readonly=False)

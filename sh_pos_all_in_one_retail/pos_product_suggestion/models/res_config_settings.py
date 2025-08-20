# Copyright (C) Softhealer Technologies.
from odoo import fields, models

class ResConfigSettiongsInhert(models.TransientModel):
    _inherit = "res.config.settings"

    pos_enable_product_suggestion = fields.Boolean(related="pos_config_id.enable_product_suggestion", readonly=False)

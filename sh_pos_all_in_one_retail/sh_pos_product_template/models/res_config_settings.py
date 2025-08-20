# Copyright (C) Softhealer Technologies.
from odoo import fields, models


class ResConfigSettiongsInhert(models.TransientModel):
    _inherit = "res.config.settings"

    pos_sh_enable_product_template = fields.Boolean(related="pos_config_id.sh_enable_product_template", readonly=False
    )

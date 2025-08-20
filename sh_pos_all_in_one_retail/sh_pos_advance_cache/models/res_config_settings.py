# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models, fields, api
    
class ResConfigSettiongsInhert(models.TransientModel):
    _inherit = "res.config.settings"

    sh_partner_upate = fields.Selection(
        related="pos_config_id.sh_partner_upate", readonly=False)
    sh_product_upate = fields.Selection(
        related="pos_config_id.sh_product_upate", readonly=False)
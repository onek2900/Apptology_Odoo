# Copyright (C) Softhealer Technologies.

from odoo import models, fields


class PosConfig(models.Model):
    _inherit = "pos.config"

    sh_enable_product_template = fields.Boolean("Enable Product Template ")

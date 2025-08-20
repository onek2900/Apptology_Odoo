# Copyright (C) Softhealer Technologies.
# Part of Softhealer Technologies.


from odoo import models, fields


class PosConfig(models.Model):
    _inherit = "pos.config"

    enable_weight = fields.Boolean(string="Enable Product Weight")
    enable_volume = fields.Boolean(string="Enable Product Volume")
    product_weight_receipt = fields.Boolean(string="Display Product Weight in Receipt")
    product_volume_receipt = fields.Boolean(string="Display Product Volume in Receipt")

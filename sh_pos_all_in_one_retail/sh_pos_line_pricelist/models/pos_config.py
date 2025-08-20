# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    sh_pricelist_for_code = fields.Many2one(
        'product.pricelist', string="Code for the selected pricelist ")
    sh_min_pricelist_value = fields.Many2one(
        'product.pricelist', string="Minimum value for pricelist")

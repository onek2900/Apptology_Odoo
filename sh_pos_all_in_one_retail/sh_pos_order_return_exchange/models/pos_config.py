# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields, models, api
from datetime import datetime, timedelta


class PosConfig(models.Model):
    _inherit = 'pos.config'

    sh_allow_return = fields.Boolean(string="Allow Return Order")
    sh_return_more_qty = fields.Boolean(
        string="Allow Return More Than Purchase Item")
    sh_return_print_receipt = fields.Boolean(
        string="Print Information In Receipt ")
    sh_allow_exchange = fields.Boolean(string="Allow Exchange Order")
    sh_exchange_print_receipt = fields.Boolean(
        string="Print Information In Receipt")


class ProductProduct(models.Model):
    _inherit = "product.product"

    sh_product_non_returnable = fields.Boolean(string="Non Returnable")
    sh_product_non_exchangeable = fields.Boolean(string="Non Exchangeable")

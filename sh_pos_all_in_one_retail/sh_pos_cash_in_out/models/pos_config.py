# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    sh_enable_cash_in_out_statement = fields.Boolean(
        "Enable Cash In/Out Statement")
    sh_enable_payment = fields.Boolean(string="Enable Payment Detail")

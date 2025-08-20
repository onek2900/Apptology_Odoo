# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models, fields, api

class PosConfig(models.Model):
    _inherit = "pos.config"

    sh_partner_upate = fields.Selection([('online','Real Time'),('on_refresh','On Refresh')],
        string="Update Customer ",default='on_refresh')
    sh_product_upate = fields.Selection([('online','Real Time'),('on_refresh','On Refresh')],
        string="Update Product ",default='on_refresh')
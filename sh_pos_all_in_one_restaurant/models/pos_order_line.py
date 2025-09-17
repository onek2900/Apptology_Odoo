# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.
# Part of Softhealer Technologies.

from odoo import models, fields, api

class OrderLine(models.Model):
    _inherit = "pos.order.line"

    topping_uuids = fields.Char(string="Topping lines")

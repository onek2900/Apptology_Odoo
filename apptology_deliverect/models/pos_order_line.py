# -*- coding: utf-8 -*-

from odoo import fields, models

class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    product_remark = fields.Text(string="Remark")
# Copyright (C) Softhealer Technologies.
# Part of Softhealer Technologies.

from odoo import models, fields

class Productinherit(models.Model):
    _inherit = 'product.template'

    sh_order_label_demo_product = fields.Boolean(string="Orderline Label")

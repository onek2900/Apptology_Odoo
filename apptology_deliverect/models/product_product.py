# -*- coding: utf-8 -*-

from odoo import models, fields
from odoo.http import request


class ProductProduct(models.Model):
    """ the deliverect configuration model"""
    _inherit = "product.product"

    name = fields.Char(string="Name")
    client_id = fields.Char(string="Client ID")
    client_secret = fields.Char(string="Client Secret")

    def action_sync_product(self):
        print('hello')
# -*- coding: utf-8 -*-
from odoo import models, fields


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    is_deliverect_pricelist = fields.Boolean(
        string='Deliverect Pricelist',
        help='If enabled, this pricelist is used for Deliverect exports.'
    )


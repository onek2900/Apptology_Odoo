# Copyright (C) Softhealer Technologies.
# -*- coding: utf-8 -*-

from odoo import models, fields


class PosConfig(models.Model):
    _inherit = 'pos.config'

    sh_pos_enable_product_variants = fields.Boolean(
        string='Enable Product Variants')
    sh_close_popup_after_single_selection = fields.Boolean(
        string='Auto close popup after single variant selection')
    sh_pos_display_alternative_products = fields.Boolean(
        string='Display Alternative product')
    sh_pos_variants_group_by_attribute = fields.Boolean(
        string='Group By Attribute', default=False)


class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'

    sh_alternative_products = fields.Many2many(
        'product.product', 'sh_table_pos_alternative_products', string='Alternative Products', domain="[('available_in_pos', '=', True)]")

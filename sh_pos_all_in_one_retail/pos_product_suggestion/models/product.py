# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.
from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = "product.product"
    
    sh_uom_line_ids = fields.One2many('sh.uom.line', 'product_id', string="UOMs")

class ProductTemplate(models.Model):
    _inherit = "product.template"

    suggestion_line = fields.One2many(
        'product.suggestion', 'product_id', string="Product Suggestion")


class ProductSuggestion(models.Model):
    _name = "product.suggestion"
    _description = "POS Product Suggestion"

    product_id = fields.Many2one('product.template')
    product_suggestion_id = fields.Many2one(
        'product.product', required=True, string="Product Suggestion")


class PosOrderInherit(models.Model):
    _inherit = 'pos.order'

    def _get_fields_for_order_line(self):
        sh_fields = super(PosOrderInherit, self)._get_fields_for_order_line()
        sh_fields.extend(['sh_uom_id'])
        
        return sh_fields


class posOrderLine(models.Model):
    _inherit = "pos.order.line"

    sh_uom_id = fields.Many2one('uom.uom', string='Unit Of Measurement',)

    def _export_for_ui(self, orderline):
        result = super()._export_for_ui(orderline)
        result["sh_uom_id"] = orderline.sh_uom_id.id
        return result





class shUOM(models.Model):

    _name = 'sh.uom.line'
    _description = 'UOM '


    uom_id = fields.Many2one('uom.uom',string='UOM',)
    price  = fields.Float("Price")
    product_id = fields.Many2one('product.product')
    uom_name  = fields.Char(related='uom_id.name')
    sh_qty  = fields.Float("Qty")

class PricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    sh_uom_id = fields.Many2one('uom.uom',string='UOM',)

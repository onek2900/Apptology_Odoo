# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ShProductBarcode(models.Model):
    _name = 'product.template.barcode'
    _description = "Product Barcode"

    product_id = fields.Many2one('product.product', 'Product', ondelete="cascade")
    name = fields.Char("Barcode", required=True, ondelete="cascade")

    @api.constrains('name')
    def check_uniqe_name(self):
        for rec in self:
            if self.env.company and self.env.company.sh_multi_barcode_unique:
                product_id = self.env['product.product'].sudo().search(['|',('barcode','=',rec.name),('barcode_line_ids.name','=',rec.name),('id','!=',rec.product_id.id)])
                if product_id:
                    raise ValidationError(_('Barcode must be unique!'))
                else:
                    barcode_id = self.env['product.template.barcode'].search([('name','=',rec.name),('id','!=',rec.id)])
                    if barcode_id:
                        raise ValidationError(_('Barcode must be unique!'))

    def _valid_field_parameter(self, field, name):
        return name in ['ondelete'] or super()._valid_field_parameter(field, name)

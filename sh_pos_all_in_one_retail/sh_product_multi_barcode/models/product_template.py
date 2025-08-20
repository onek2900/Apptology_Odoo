# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ShProductTemplate(models.Model):
    _inherit = 'product.template'

    barcode_line_ids = fields.One2many(
        related='product_variant_ids.barcode_line_ids', readonly=False, ondelete="cascade")

    @api.constrains('barcode','barcode_line_ids')
    def check_uniqe_name(self):
        for rec in self:
            if self.env.company and self.env.company.sh_multi_barcode_unique:
                multi_barcode_id = self.env['product.template.barcode'].search([('name', '=', rec.barcode)])
                if multi_barcode_id:
                    raise ValidationError(_(
                        'Barcode must be unique!'))

    @api.model_create_multi
    def create(self, vals_list):
        ''' Store the initial standard price in order to be able to retrieve the cost of a product template for a given date'''
        templates = super(ShProductTemplate, self).create(vals_list)
        # This is needed to set given values to first variant after creation
        for template, vals in zip(templates, vals_list):
            related_vals = {}
            if vals.get('barcode_line_ids'):
                related_vals['barcode_line_ids'] = vals['barcode_line_ids']
            if related_vals:
                template.write(related_vals)
        return templates
    def _valid_field_parameter(self, field, name):
        return name in ['ondelete'] or super()._valid_field_parameter(field, name)

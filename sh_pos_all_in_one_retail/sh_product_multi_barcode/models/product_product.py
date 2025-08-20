# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ShProduct(models.Model):
    _inherit = 'product.product'

    barcode_line_ids = fields.One2many(
        'product.template.barcode', 'product_id', 'Barcode Lines', ondelete="cascade")

    @api.model
    def _name_search(self, name, domain=None, operator='ilike', limit=None, order=None):
        domain = domain or []
        res = super(ShProduct, self)._name_search(name, domain, operator, limit, order)
        mutli_barcode_search = list(self._search(
            [('barcode_line_ids', '=', name)] + domain, limit=limit))
        if mutli_barcode_search:
            return res + mutli_barcode_search
        return res

    @api.constrains('barcode','barcode_line_ids')
    def check_uniqe_name(self):
        for rec in self:
            if self.env.company and self.env.company.sh_multi_barcode_unique:
                multi_barcode_id = self.env['product.template.barcode'].search([('name', '=', rec.barcode)])
                if multi_barcode_id:
                    raise ValidationError(_(
                        'Barcode must be unique!'))
    def _valid_field_parameter(self, field, name):
        return name in ['ondelete'] or super()._valid_field_parameter(field, name)

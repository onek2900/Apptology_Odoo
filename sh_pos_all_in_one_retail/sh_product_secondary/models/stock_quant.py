# -*- coding: UTF-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields

class ShStockQuant(models.Model):
    _inherit = 'stock.quant'

    sh_secondary_unit_qty = fields.Float(
        ' On Hand',
        compute='_compute_secondary_unit_on_hand_qty'
    )
    sh_secondary_unit = fields.Many2one(
        'uom.uom',
        'Secondary UOM',
        related='product_id.sh_secondary_uom'
    )

    def _compute_secondary_unit_on_hand_qty(self):
        if self:
            for rec in self:
                if rec.sh_secondary_unit:
                    rec.sh_secondary_unit_qty = rec.product_uom_id._compute_quantity(
                        rec.quantity, rec.sh_secondary_unit)
                else:
                    rec.sh_secondary_unit_qty = 00

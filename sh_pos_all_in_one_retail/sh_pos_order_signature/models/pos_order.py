# Copyright (C) Softhealer Technologies.
# Part of Softhealer Technologies.

from odoo import fields, models

class PosOrder(models.Model):
    _inherit = "pos.order"

    signature = fields.Binary(string="Signature")
    signature_name = fields.Char(string="Name : ")
    signature_date = fields.Date(string="Date : ")

    def _order_fields(self, ui_order):
        res = super()._order_fields(ui_order)
        res.update({
            'signature': ui_order.get('signature') if ui_order.get('signature') else False,
            'signature_name': ui_order.get('signature_name') or False,
            'signature_date': ui_order.get('signature_date') or False
        })
        return res

    def _export_for_ui(self, order):
        res = super()._export_for_ui(order)
        if order.signature:
            res['signature'] = order.signature
        if order.signature_date:
            res['signature_date'] = order.signature_date
        if order.signature_name:
            res['signature_name'] = order.signature_name

        return res

# coding: utf-8

from odoo import fields, models


class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    is_deliverect_payment_method = fields.Boolean(string="Deliverect Payment Method")
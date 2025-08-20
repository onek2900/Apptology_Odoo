# Copyright (C) Softhealer Technologies.
# Part of Softhealer Technologies.

from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    sh_pos_order_number = fields.Boolean(
        string="Display Order Number")
    sh_pos_receipt_bacode_qr = fields.Boolean(
        string="Display Barcode / QrCode")
    sh_pos_receipt_barcode_qr_selection = fields.Selection(
        [('barcode', 'Barcode'), ('qr', 'QrCode')], default='barcode')
    sh_pos_receipt_invoice = fields.Boolean(string="Display Invoice Number")
    sh_pos_receipt_customer_detail = fields.Boolean(
        string="Display Customer Detail")
    sh_pos_receipt_customer_name = fields.Boolean(
        string="Display Customer Name")
    sh_pos_receipt_customer_address = fields.Boolean(
        string="Display Customer Address")
    sh_pos_receipt_customer_mobile = fields.Boolean(
        string="Display Customer Mobile")
    sh_pos_receipt_customer_phone = fields.Boolean(
        string="Display Customer Phone")
    sh_pos_receipt_customer_email = fields.Boolean(
        string="Display Customer Email")
    sh_pos_vat = fields.Boolean(string="Display Customer Vat")
    sh_pos_vat_name = fields.Char(string='vat name')
    sh_enable_a3_receipt = fields.Boolean(string="Use A3 receipts")
    sh_enable_a4_receipt = fields.Boolean(string="Use A4 receipts")
    sh_enable_a5_receipt = fields.Boolean(string="Use A5 receipts")
    sh_default_receipt = fields.Selection([
        ('a3_size','A3 Size'),
        ('a4_size','A4 Size'),
        ('a5_size','A5 Size'),
    ],string="Standard Receipts")

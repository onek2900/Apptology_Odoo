# Copyright (C) Softhealer Technologies.
# Part of Softhealer Technologies.

from odoo import fields, models


class ResConfigSettiongsInhert(models.TransientModel):
    _inherit = "res.config.settings"

    pos_sh_pos_order_number = fields.Boolean(
        related="pos_config_id.sh_pos_order_number",
        string="Display Order Number",
        readonly=False,
    )
    pos_sh_pos_receipt_bacode_qr = fields.Boolean(
        related="pos_config_id.sh_pos_receipt_bacode_qr",
        string="Display Barcode / QrCode",
        readonly=False,
    )
    pos_sh_pos_receipt_barcode_qr_selection = fields.Selection(
        related="pos_config_id.sh_pos_receipt_barcode_qr_selection", readonly=False
    )
    pos_sh_pos_receipt_invoice = fields.Boolean(
        related="pos_config_id.sh_pos_receipt_invoice",
        string="Display Invoice Number",
        readonly=False,
    )
    pos_sh_pos_receipt_customer_detail = fields.Boolean(
        related="pos_config_id.sh_pos_receipt_customer_detail",
        string="Display Customer Detail",
        readonly=False,
    )
    pos_sh_pos_receipt_customer_name = fields.Boolean(
        related="pos_config_id.sh_pos_receipt_customer_name",
        string="Display Customer Name",
        readonly=False,
    )
    pos_sh_pos_receipt_customer_address = fields.Boolean(
        related="pos_config_id.sh_pos_receipt_customer_address",
        string="Display Customer Address",
        readonly=False,
    )
    pos_sh_pos_receipt_customer_mobile = fields.Boolean(
        related="pos_config_id.sh_pos_receipt_customer_mobile",
        string="Display Customer Mobile",
        readonly=False,
    )
    pos_sh_pos_receipt_customer_phone = fields.Boolean(
        related="pos_config_id.sh_pos_receipt_customer_phone",
        string="Display Customer Phone",
        readonly=False,
    )
    pos_sh_pos_receipt_customer_email = fields.Boolean(
        related="pos_config_id.sh_pos_receipt_customer_email",
        string="Display Customer Email",
        readonly=False,
    )
    pos_sh_pos_vat = fields.Boolean(
        related="pos_config_id.sh_pos_vat",
        string="Display Customer Vat",
        readonly=False,
    )
    pos_sh_pos_vat_name = fields.Char(
        related="pos_config_id.sh_pos_vat_name", string="vat name", readonly=False
    )
    pos_sh_enable_a3_receipt = fields.Boolean(
        related="pos_config_id.sh_enable_a3_receipt", readonly=False
    )
    pos_sh_enable_a4_receipt = fields.Boolean(
        related="pos_config_id.sh_enable_a4_receipt", readonly=False
    )
    pos_sh_enable_a5_receipt = fields.Boolean(
        related="pos_config_id.sh_enable_a5_receipt", readonly=False
    )
    pos_sh_default_receipt = fields.Selection(
        related="pos_config_id.sh_default_receipt", readonly=False
    )

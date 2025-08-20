# Copyright (C) Softhealer Technologies.
# Part of Softhealer Technologies.

from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    sh_enable_order_signature = fields.Boolean(
        string="Allow Signature")
    sh_enable_name = fields.Boolean(string="Allow Name With Signature")
    sh_enable_date = fields.Boolean(string="Allow Date With Signature")
    sh_display_signature_detail = fields.Boolean(
        string="Display Signature Detail In Receipt")
    sh_display_signature = fields.Boolean(
        string="Display Signature In Receipt")
    sh_display_name = fields.Boolean(string="Display Name In Receipt")
    sh_display_date = fields.Boolean(string="Display Date In Receipt")



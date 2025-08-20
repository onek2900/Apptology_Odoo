# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields, api, _

class PosConfigInherit(models.Model):
    _inherit = 'pos.config'

    sh_enable_z_report = fields.Boolean(string="Allow to Print Z Report")
    sh_display_category_wise_detail = fields.Boolean(string="Display Category Wise Detail")
    sh_display_product_wise_detail = fields.Boolean(string="Display Product Wise Detail")
    sh_display_customer_wise_detail = fields.Boolean(string="Display Customer Wise Detail")
    sh_display_payment_detail = fields.Boolean(string="Display Payment Detail")
    sh_allow_z_report_type = fields.Selection([('receipt','Receipt'),('pdf','Pdf'),('both','Both')], string="Z Report Type", default="pdf", required=True)
    sh_allow_posted_session_report = fields.Boolean(string="Allow Posted Session Report")
    
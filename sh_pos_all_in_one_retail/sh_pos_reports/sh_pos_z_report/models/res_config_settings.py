# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields, api

class ResConfigSettiongsInhert(models.TransientModel):
    _inherit = "res.config.settings"

    pos_sh_enable_z_report = fields.Boolean(
        related="pos_config_id.sh_enable_z_report", readonly=False)
    pos_sh_display_category_wise_detail = fields.Boolean(related="pos_config_id.sh_display_category_wise_detail", readonly=False)
    pos_sh_display_product_wise_detail = fields.Boolean(related="pos_config_id.sh_display_product_wise_detail", readonly=False)
    pos_sh_display_customer_wise_detail = fields.Boolean(related="pos_config_id.sh_display_customer_wise_detail", readonly=False)
    pos_sh_display_payment_detail = fields.Boolean(related="pos_config_id.sh_display_payment_detail", readonly=False)
    pos_sh_allow_z_report_type = fields.Selection(related="pos_config_id.sh_allow_z_report_type", readonly=False, required=True)
    pos_sh_allow_posted_session_report = fields.Boolean(related="pos_config_id.sh_allow_posted_session_report", readonly=False)
        
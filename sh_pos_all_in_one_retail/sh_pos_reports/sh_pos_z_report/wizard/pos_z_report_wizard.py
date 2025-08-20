# -*- coding: utf-8 -*-

from odoo import fields, models


class PosDetails(models.TransientModel):
    _name = 'pos.z.report.wizard'
    _description = 'Point of Sale Z Report'

    sh_session_id = fields.Many2many('pos.session', string="Session", required=True)
    sh_display_category_wise_detail = fields.Boolean(string="Display Category Wise Detail")
    sh_display_product_wise_detail = fields.Boolean(string="Display Product Wise Detail")
    sh_display_customer_wise_detail = fields.Boolean(string="Display Customer Wise Detail")
    sh_display_payment_detail = fields.Boolean(string="Display Payment Detail")

    def generate_report(self):
        data = {'pos_session_id':self.sh_session_id.ids, 'category_wise':self.sh_display_category_wise_detail, 'product_wise':self.sh_display_product_wise_detail, 'customer_wise':self.sh_display_customer_wise_detail, 'payment_wise':self.sh_display_payment_detail}
        return self.env.ref('sh_pos_all_in_one_retail.sh_pos_z_report_backend').report_action([], data=data)

# -*- coding: utf-8 -*-
from odoo import models


class PosSession(models.Model):
    """Inherit to load new fields to pos"""
    _inherit = 'pos.session'

    def _loader_params_pos_order(self):
        """Load the fields to pos order"""
        result = super()._loader_params_pos_order()
        result['search_params']['fields']+=['order_type','order_payment_type','note','channel_discount',
                                            'channel_service_charge','channel_delivery_charge','channel_tip_amount',
                                            'bag_fee',
                                            'channel_total_amount','delivery_note','channel_order_reference',
                                            'pickup_time','delivery_time','channel_name','customer_name',
                                            'customer_company_name','customer_email','customer_note','channel_tax']
        return result
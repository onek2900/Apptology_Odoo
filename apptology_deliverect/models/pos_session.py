# -*- coding: utf-8 -*-

from odoo import models


class PosSession(models.Model):
    """Inheriting the pos session"""
    _inherit = 'pos.session'

    def _loader_params_pos_order(self):
        """Load the fields to pos order"""
        print("Loading pos order fields")
        result = super()._loader_params_pos_order()
        result['search_params']['fields']+=['order_type','order_payment_type','note']
        return result
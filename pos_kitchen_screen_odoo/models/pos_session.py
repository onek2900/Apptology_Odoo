# -*- coding: utf-8 -*-

from odoo import models


class PosSession(models.Model):
    """Inheriting the pos session"""
    _inherit = 'pos.session'

    def _pos_ui_models_to_load(self):
        """Pos ui models to load

        Keep original order and append extra models at the end to avoid
        breaking dependencies (e.g., 'pos.combo' before 'pos.combo.line').
        """
        result = list(super()._pos_ui_models_to_load())
        for model in ['pos.order', 'pos.order.line']:
            if model not in result:
                result.append(model)
        return result

    def _loader_params_pos_order(self):
        """Load the fields to pos order"""
        return {'search_params': {
            'domain': [],
            'fields': ['name', 'date_order', 'pos_reference',
                       'partner_id', 'lines', 'order_status', 'order_ref',
                       'table_id',
                       'is_cooking', 'kitchen_new_line_summary', 'kitchen_new_line_count', 'kitchen_send_logs']}}

    def _get_pos_ui_pos_order(self, params):
        """Get pos ui pos order"""
        return self.env['pos.order'].search_read(
            **params['search_params'])

    def _loader_params_pos_order_line(self):
        """Load the fields to pos order line"""
        return {'search_params': {'domain': [],
                                  'fields': ['product_id', 'qty',
                                             'order_status', 'order_ref',
                                             'customer_id', 'full_product_name', 'note',
                                             'price_subtotal', 'total_cost',
                                             'sh_is_topping', 'product_sh_is_topping',
                                             'kitchen_ticket_uid']}}

    def _get_pos_ui_pos_order_line(self, params):
        """Get pos ui pos order line"""
        return self.env['pos.order.line'].search_read(
            **params['search_params'])

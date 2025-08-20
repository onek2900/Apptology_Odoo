# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import  models


class PosSessionInherit(models.Model):
    _inherit = 'pos.session'

    def _loader_params_pos_session(self):
        result = super(PosSessionInherit,
                       self)._loader_params_pos_session()
        result['search_params']['fields'].extend(
            ["cash_register_total_entry_encoding", "cash_register_balance_end", "cash_register_balance_end_real", "cash_register_balance_start"])
        return result

    def _pos_data_process(self, loaded_data):
        super()._pos_data_process(loaded_data)
        loaded_data['payment_method_by_id'] = {
            payment['id']: payment for payment in loaded_data['pos.payment.method']}

    def _pos_ui_models_to_load(self):
        result = super()._pos_ui_models_to_load()
        # new_model = 'sh.cash.in.out'
        if 'sh.cash.in.out' not in result:
            result.append('sh.cash.in.out')
        if 'pos.payment' not in result:
            result.append('pos.payment')
        return result

    def _loader_params_sh_cash_in_out(self):
        return {'search_params': {'domain': [], 'fields': [], 'load': False}}

    def _get_pos_ui_sh_cash_in_out(self, params):
        return self.env['sh.cash.in.out'].search_read(**params['search_params'])

    def _loader_params_pos_payment(self):
        return {'search_params': {'domain': [], 'fields': [], 'load': False}}

    def _get_pos_ui_pos_payment(self, params):
        return self.env['pos.payment'].search_read([('session_id', '=', self.id)])

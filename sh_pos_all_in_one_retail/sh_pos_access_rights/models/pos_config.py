# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    disable_payment_id = fields.Many2one(
        'res.groups', compute='_compute_access_rights', string='POS - Disable Payment')

    group_select_customer = fields.Many2one(
        'res.groups', compute='_compute_access_rights', string='POS - Customer Selection')

    group_disable_discount = fields.Many2one(
        'res.groups', compute='_compute_access_rights', string='POS - Disable Discount Button')

    group_disable_qty = fields.Many2one(
        'res.groups', compute='_compute_access_rights', string='POS - Disable Qty Button')

    group_disable_price = fields.Many2one(
        'res.groups', compute='_compute_access_rights', string='POS - Disable Price Button')

    group_disable_plus_minus = fields.Many2one(
        'res.groups', compute='_compute_access_rights', string='POS - Disable Plus-Minus')

    group_disable_numpad = fields.Many2one(
        'res.groups', compute='_compute_access_rights', string='POS - Disable Numpad')

    group_disable_hide_orders = fields.Many2one('res.groups', compute='_compute_access_rights', string='POS - Disable New/Delete Orders')

    group_disable_remove = fields.Many2one('res.groups', compute='_compute_access_rights', string='POS - Disable Remove Button')


    def _compute_access_rights(self):
        for rec in self:
            rec.disable_payment_id = self.env.ref(
                'sh_pos_all_in_one_retail.group_disable_payment')
            rec.group_select_customer = self.env.ref(
                'sh_pos_all_in_one_retail.group_select_customer')
            rec.group_disable_discount = self.env.ref(
                'sh_pos_all_in_one_retail.group_disable_discount')
            rec.group_disable_qty = self.env.ref(
                'sh_pos_all_in_one_retail.group_disable_qty')
            rec.group_disable_price = self.env.ref(
                'sh_pos_all_in_one_retail.group_disable_price')
            rec.group_disable_plus_minus = self.env.ref(
                'sh_pos_all_in_one_retail.group_disable_plus_minus')
            rec.group_disable_numpad = self.env.ref(
                'sh_pos_all_in_one_retail.group_disable_numpad')
            rec.group_disable_hide_orders = self.env.ref(
                'sh_pos_all_in_one_retail.group_disable_hide_orders')
            rec.group_disable_remove = self.env.ref(
                'sh_pos_all_in_one_retail.group_disable_remove')

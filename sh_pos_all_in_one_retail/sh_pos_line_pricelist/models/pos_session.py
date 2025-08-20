# Copyright (C) Softhealer Technologies.
# Part of Softhealer Technologies.

from odoo import models


class PosSessionInherit(models.Model):
    _inherit = "pos.session"

    def _pos_data_process(self, loaded_data):
        super()._pos_data_process(loaded_data)
        loaded_data['all_pricelists'] = self.env['product.pricelist'].search_read()
        loaded_data['pricelist_by_id'] = {
            pricelist['id']: pricelist for pricelist in self.env['product.pricelist'].search_read()}
        loaded_data['all_pricelists_item'] = self.env['product.pricelist.item'].search_read()
        loaded_data['pricelist_item_by_id'] = {
            pricelistItem['id']: pricelistItem for pricelistItem in self.env['product.pricelist.item'].search_read()}

# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models


class PosSessionInherit(models.Model):
    _inherit = 'pos.session'

    def _pos_data_process(self, loaded_data):
        super()._pos_data_process(loaded_data)
        if self.config_id and self.config_id.sh_display_stock:
            quants = self.sh_load_quants()
            location_by_id = {}
            if quants['location_details']:
                new_dic = {}
                for quant in quants['location_details']:
                    location_by_id[quant['location_id']] = {'id': quant['location_id'], 'name': quant['location_name']}
                    if quant['product_id'] in new_dic:
                        new_dic[quant['product_id']].append(quant)
                    else:
                        new_dic[quant['product_id']] = [quant]
                loaded_data['quant_by_product_id'] = new_dic
            loaded_data['location_by_id'] = location_by_id

    def sh_load_quants(self):
        result = {}
        if self.config_id and self.config_id.sh_display_stock:
            self.env.cr.execute(""" SELECT quant.id, quant.quantity, quant.product_id, quant.location_id, location.name as location_name, location.company_id, location.warehouse_id, warehouse.name as warehouse_name FROM stock_quant quant
                                JOIN stock_location location ON quant.location_id = location.id 
                                JOIN stock_warehouse warehouse ON warehouse.id = location.warehouse_id 
                                JOIN res_company company ON company.id = location.company_id
                                WHERE company.id = %s AND location.usage = 'internal' """,[self.env.company.id])
            quants = self.env.cr.dictfetchall()
            result['location_details'] = quants
        return result

    def _loader_params_product_product(self):
        result = super(PosSessionInherit,
                       self)._loader_params_product_product()
        result['search_params']['fields'].extend(["type", "qty_available"])
        return result

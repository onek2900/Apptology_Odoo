# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models


class PosSessionInherit(models.Model):
    _inherit = 'pos.session'

    def _loader_params_product_product(self):
        result = super(PosSessionInherit,
                       self)._loader_params_product_product()
        result['search_params']['fields'].extend(
            ["sh_product_non_returnable", "sh_product_non_exchangeable"])
        return result

    def load_all_pos_order_lines(self):
        self.env.cr.execute(""" SELECT  ol.product_id,ol.id ,ol.qty ,ol.price_unit, ol.discount, ol.price_subtotal,ol.order_id, ol.price_subtotal_incl, ol.sh_return_qty, ol.sh_exchange_qty FROM pos_order_line ol
                            INNER JOIN pos_order pos ON (pos.id=ol.order_id)
                            """)
        lines = self.env.cr.dictfetchall()
        return lines
    
    def sh_get_line_data_by_id(self, ids):
        self.env.cr.execute(f""" SELECT  ol.product_id,ol.id ,ol.qty ,ol.price_unit, ol.discount, ol.price_subtotal,ol.order_id, ol.price_subtotal_incl, ol.sh_return_qty, ol.sh_exchange_qty FROM pos_order_line ol where id IN %(sh_line_ids)s""", {
            'sh_line_ids': tuple(ids)
        } )
        lines = self.env.cr.dictfetchall()
        return lines

    def get_order_fields(self):
        result =  super().get_order_fields()
        result.extend(['pos_order.is_return_order', 'pos_order.return_status', 'pos_order.old_pos_reference'])
        return result
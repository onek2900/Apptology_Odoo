# Copyright (C) Softhealer Technologies.
# Part of Softhealer Technologies.

from odoo import models, fields
from odoo.osv.expression import OR


class PosConfig(models.Model):
    _inherit = 'pos.config'

    enable_order_line_label = fields.Boolean(string='Enable Order Line Label ')
    enabel_delete_label_with_product = fields.Boolean(
        string='Delete Label with Lines')
    enable_order_line_label_in_receipt = fields.Boolean(
        string='Print Order Line Label in Receipt')

    def _get_available_product_domain(self):
        domain = super()._get_available_product_domain()
        if self.limit_categories and self.iface_available_categ_ids:
            domain = OR([domain, [('sh_order_label_demo_product','=', True)]])
        return domain

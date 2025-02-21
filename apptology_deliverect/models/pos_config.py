# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PosConfig(models.Model):
    _inherit = 'pos.config'

    auto_approve = fields.Boolean(string="Auto Approve", help="Automatically approve all orders from Deliverect")

    def toggle_approve(self):
        print('toggle',self)
        if self.auto_approve:
            self.auto_approve = False
        else:
            self.auto_approve = True
        print(self.auto_approve)

    @api.model_create_multi
    def create(self, vals_list):
        configs = super().create(vals_list)
        deliverect_payment_method = self.env.ref("apptology_deliverect.pos_payment_method_deliverect")
        configs.write({
            'payment_method_ids': [fields.Command.link(deliverect_payment_method.id)]
        })
        return configs

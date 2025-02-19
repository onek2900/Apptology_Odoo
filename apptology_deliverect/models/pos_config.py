# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PosConfig(models.Model):
    _inherit = 'pos.config'

    auto_approve = fields.Boolean(string="Auto Approve", help="Automatically approve all orders from Deliverect")

    def toggle_approve(self):
        if self.auto_approve:
            self.auto_approve = False
        else:
            self.auto_approve = True

# Copyright (C) Softhealer Technologies.
# Part of Softhealer Technologies.

from odoo import models, fields

class PosConfigInherit(models.Model):
    _inherit = "pos.config"

    sh_dispaly_purchase_btn = fields.Boolean("Enable Purchase Order")
    select_purchase_state = fields.Selection(
        [('rfq', 'RFQ'), ('purchase_order', 'Purchase Order')], string="Select Order State", default="rfq")

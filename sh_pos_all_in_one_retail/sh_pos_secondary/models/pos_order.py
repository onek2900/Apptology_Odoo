# Copyright (C) Softhealer Technologies.
# Part of Softhealer Technologies.

from odoo import models

class ShPosOrder(models.Model):
    _inherit = "pos.order"

    def _export_for_ui(self, order):
        res = super()._export_for_ui(order)
        # if order:
        return res

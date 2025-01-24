# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_pos_nearpay = fields.Boolean(string="Nearpay Payment Terminal", help="You can able to use nearpay payment gateway",)

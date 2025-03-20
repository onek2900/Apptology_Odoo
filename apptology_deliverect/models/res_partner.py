# -*- coding: utf-8 -*-
from odoo import models, fields


class ResPartner(models.Model):
    """Inherit res.partner to add channel_id field."""
    _inherit = "res.partner"

    channel_id = fields.Char(string='Channel', help='Channel ID the of partner')

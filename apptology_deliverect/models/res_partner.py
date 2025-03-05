# -*- coding: utf-8 -*-
import logging
from odoo import models, fields

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    """Inherit res.partner to add channel_id field."""
    _inherit = "res.partner"

    channel_id = fields.Char()

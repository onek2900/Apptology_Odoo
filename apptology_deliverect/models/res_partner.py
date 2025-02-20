# -*- coding: utf-8 -*-

import requests
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    channel_id = fields.Integer()

# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models, fields, api

class PosSession(models.Model):
    _inherit = "pos.session"

    def sh_load_model(self, Model):
        return self._load_model(Model)
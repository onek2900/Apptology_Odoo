# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models, fields
from odoo.exceptions import UserError


class POSSession(models.Model):
    _inherit = "pos.session"

    def _auto_validate_pos_session(self):  # Cron Method
        for rec in self.search([('state', 'in', ('opened', 'closing_control'))]):
            if rec:
                try:
                    if rec.cash_control:
                        rec.action_pos_session_closing_control()
                        rec.action_pos_session_validate()
                    else:
                        rec.action_pos_session_closing_control()

                except UserError as e:
                    if e:
                        self.env['log.track'].sudo().create({'date': fields.Date.today(),
                                                             'session_id': rec.id,
                                                             'error': e})


class LogTrack(models.Model):
    _name = 'log.track'
    _description = "Log Track"
    _rec_name = 'session_id'

    date = fields.Date("Date")
    session_id = fields.Many2one('pos.session', string="Session")
    error = fields.Char("Error")

# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

class PosConfig(models.Model):
    _inherit = 'pos.config'

    sh_enable_order_reprint = fields.Boolean(string="Allow To Reprint Order")
    sh_enable_re_order = fields.Boolean(string="Allow To ReOrder")
    sh_enable_order_list = fields.Boolean(string="Enable Order List")
    sh_load_order_by = fields.Selection(
        [('all', 'All'), ('session_wise', 'Session Wise'), ('day_wise', 'Day Wise')], string="Load Order By", default='all', required=True)
    sh_session_wise_option = fields.Selection(
        [('current_session', 'Current Session'), ('last_no_session', 'Last No Of Session')], default='current_session', string="Session Of")
    sh_day_wise_option = fields.Selection(
        [('current_day', 'Current Day'), ('last_no_day', 'Last No Of Days')], default='current_day', string="Day Of")
    sh_last_no_days = fields.Integer(string="Last No Of Days")
    sh_last_no_session = fields.Integer(string="Last No Of Session")
    sh_how_many_order_per_page = fields.Integer(
        string="How Many Orders You Want to display Per Page ? ", default=30)

    @api.constrains('sh_last_no_session', 'sh_last_no_days')
    def _check_validity_constrain(self):
        """ verifies if record.to_hrs is earlier than record.from_hrs. """
        for record in self:
            if record and record.sh_last_no_days < 0:
                raise ValidationError(
                    _('Last Number Of Days must be positive.'))
            if record and record.sh_last_no_session < 0:
                raise ValidationError(
                    _('Last Number Of Sessions must be positive.'))

    @api.constrains('sh_how_many_order_per_page')
    def _onchange_sh_how_many_order_per_page(self):
        if self.sh_how_many_order_per_page:
            if self.sh_how_many_order_per_page < 0:
                raise ValidationError(_('Order Per Page must be positive'
                                        ))
        if self.sh_how_many_order_per_page == 0:
            raise ValidationError(_('Order Per Page must be more than 0'
                                    ))

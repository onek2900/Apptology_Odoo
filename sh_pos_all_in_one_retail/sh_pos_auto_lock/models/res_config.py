# Copyright (C) Softhealer Technologies.
# Part of Softhealer Technologies.

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class PosConfig(models.Model):
    _inherit = 'pos.config'

    sh_enable_auto_lock = fields.Boolean("Enable POS Auto Lock")
    sh_lock_timer = fields.Integer(string="Time Interval (In Second)")

    @api.constrains('sh_lock_timer')
    def _check_validity_constrain(self):
        """ verifies if record.to_hrs is earlier than record.from_hrs. """
        for record in self:
            if record and record.sh_lock_timer < 0:
                raise ValidationError(
                    _('Time Interval Must be Position.'))

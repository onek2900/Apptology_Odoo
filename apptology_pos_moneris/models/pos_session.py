
# -*- coding: utf-8 -*-
import json
import logging
from datetime import datetime

import requests
from odoo import models

_logger = logging.getLogger(__name__)


class PosSession(models.Model):
    _inherit = 'pos.session'

    def write(self, vals):
        res = super().write(vals)
        # Trigger sync when a session transitions to 'opened'
        if 'state' in vals and vals.get('state') == 'opened':
            for session in self:
                try:
                    session._moneris_sync_on_open()
                except Exception as e:
                    _logger.exception("Moneris sync on session open failed for session %s: %s", session.name, e)
        return res

    def _moneris_sync_on_open(self):
        """Called when a POS session is opened. For each Moneris payment method
        on the POS config, trigger a SYNC with the terminal.
        """
        self.ensure_one()
        config = self.config_id
        if not config:
            return

        moneris_pms = config.payment_method_ids.filtered(lambda pm: pm.use_payment_terminal == 'moneris')
        if not moneris_pms:
            _logger.info("No Moneris payment methods on POS config '%s'; skipping sync.", config.display_name)
            return

        for pm in moneris_pms:
            try:
                pm._moneris_sync_terminal(self)
            except Exception as e:
                _logger.exception("Moneris sync failed for terminal on payment method '%s': %s", pm.display_name, e)



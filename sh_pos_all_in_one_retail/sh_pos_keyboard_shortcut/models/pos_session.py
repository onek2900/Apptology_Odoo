# -*- coding: utf-8 -*-

from odoo import models

import logging

_logger = logging.getLogger(__name__)


class PosSession(models.Model):
    _inherit = "pos.session"

    def _pos_ui_models_to_load(self):
        result = super()._pos_ui_models_to_load()
        result.append("sh.keyboard.key.temp")
        result.append("sh.pos.keyboard.shortcut")
        return result

    def _get_pos_ui_sh_keyboard_key_temp(self, params):
        orders = self.env["sh.keyboard.key.temp"].search_read(**params["search_params"])
        return orders

    def _loader_params_sh_keyboard_key_temp(self):
        return {
            "search_params": {
                "domain": [],
                "fields": ["name", "sh_key_ids"],
            },
        }

    def _get_pos_ui_sh_pos_keyboard_shortcut(self, params):
        orders = self.env["sh.pos.keyboard.shortcut"].search_read(
            **params["search_params"]
        )
        return orders

    def _loader_params_sh_pos_keyboard_shortcut(self):
        return {
            "search_params": {
                "domain": [],
                "fields": [
                    "sh_key_ids",
                    "sh_shortcut_screen",
                    "config_id",
                    "payment_method_id",
                    "sh_payment_shortcut_screen_type",
                    "sh_shortcut_screen_type",
                ],
            },
        }

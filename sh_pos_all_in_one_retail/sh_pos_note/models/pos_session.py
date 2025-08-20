# Copyright (C) Softhealer Technologies.
# Part of Softhealer Technologies.

from odoo import models


class PosSessionInherit(models.Model):
    _inherit = "pos.session"

    def _pos_ui_models_to_load(self):
        result = super()._pos_ui_models_to_load()

        if "pre.define.note" not in result:
            result.append("pre.define.note")

        return result

    def _loader_params_pre_define_note(self):
        return {"search_params": {"domain": [], "fields": [], "load": False}}

    def _get_pos_ui_pre_define_note(self, params):
        return self.env["pre.define.note"].search_read(**params["search_params"])

    def _pos_data_process(self, loaded_data):
        super()._pos_data_process(loaded_data)

        loaded_data["pre_defined_note_data_dict"] = {
            note_data["id"]: note_data for note_data in loaded_data["pre.define.note"]
        }
        loaded_data["all_note_names"] = [
            note_data["name"] for note_data in loaded_data["pre.define.note"]
        ]

# Copyright (C) Softhealer Technologies.
from odoo import fields, models, api


class PreDefineNote(models.Model):
    _name = "pre.define.note"
    _description = "Pre Define Note"
    _order = "name desc"

    name = fields.Char("Note", translate=True)

    @api.model
    def sh_create_note(self, vals):
        created_note = self.create(vals)
        note_dict = {"id": created_note.id, "name": created_note.name}
        return note_dict

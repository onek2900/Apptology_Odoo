from odoo import api, models

from .ir_translation import debrand

class Base(models.AbstractModel):

    _inherit = "base"

    def get_view(self, view_id=None, view_type="form", **options):
        res = super().get_view(view_id=view_id, view_type=view_type, **options)
        res["arch"] = debrand(self.env, res["arch"], is_code=True)
        return res
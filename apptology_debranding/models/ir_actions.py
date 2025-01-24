from odoo import models


class IrActions(models.Model):
    _inherit = "ir.actions.act_window"

    def read(self, fields=None, load="_classic_read"):
        results = super(IrActions, self).read(
            fields=fields, load=load
        )
        if not fields or "help" in fields:
            params = self.env["ir.config_parameter"].get_debranding_parameters()
            new_name = params.get("apptology_debranding.new_name")
            for res in results:
                if isinstance(res, dict) and res.get("help"):
                    res["help"] = res["help"].replace("Odoo", new_name)
        return results
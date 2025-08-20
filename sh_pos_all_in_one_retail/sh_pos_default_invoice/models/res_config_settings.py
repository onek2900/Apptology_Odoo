from odoo import models, fields

class ResConfigSettiongsInhert(models.TransientModel):
    _inherit = "res.config.settings"

    pos_sh_enable_default_invoice = fields.Boolean(
        related="pos_config_id.sh_enable_default_invoice", readonly=False)

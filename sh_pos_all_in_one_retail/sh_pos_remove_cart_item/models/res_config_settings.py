# Part of Softhealer Technologies.

from odoo import models, fields


class ResConfigSettiongsInhert(models.TransientModel):
    _inherit = "res.config.settings"

    pos_sh_remove_all_item = fields.Boolean(related="pos_config_id.sh_remove_all_item", readonly=False)
    sh_validation_to_remove_all_item  = fields.Boolean(related="pos_config_id.sh_validation_to_remove_all_item",readonly=False)
    sh_validation_to_remove_single_item = fields.Boolean(related="pos_config_id.sh_validation_to_remove_single_item", readonly=False)
    
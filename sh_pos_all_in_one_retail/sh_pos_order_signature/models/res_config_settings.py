# Copyright (C) Softhealer Technologies.
# Part of Softhealer Technologies.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_sh_enable_order_signature = fields.Boolean(related="pos_config_id.sh_enable_order_signature", string="Allow Signature", readonly=False)
    pos_sh_enable_name = fields.Boolean(related="pos_config_id.sh_enable_name", string="Allow Name With Signature", readonly=False)
    pos_sh_enable_date = fields.Boolean(related="pos_config_id.sh_enable_date", string="Allow Date With Signature", readonly=False)
    pos_sh_display_signature_detail = fields.Boolean(related="pos_config_id.sh_display_signature_detail", string="Display Signature Detail In Receipt", readonly=False)
    pos_sh_display_signature = fields.Boolean(related="pos_config_id.sh_display_signature", string="Display Signature In Receipt", readonly=False)
    pos_sh_display_name = fields.Boolean(related="pos_config_id.sh_display_name", string="Display Name In Receipt", readonly=False)
    pos_sh_display_date = fields.Boolean(related="pos_config_id.sh_display_date", string="Display Date In Receipt" ,readonly=False)

# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models, fields

class PosConfig(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_sh_enable_order_reprint = fields.Boolean(related="pos_config_id.sh_enable_order_reprint", readonly=False)
    pos_sh_enable_re_order = fields.Boolean(related="pos_config_id.sh_enable_re_order", readonly=False)
    pos_sh_enable_order_list = fields.Boolean(related="pos_config_id.sh_enable_order_list", readonly=False)
    pos_sh_load_order_by = fields.Selection(related="pos_config_id.sh_load_order_by", readonly=False)
    pos_sh_session_wise_option = fields.Selection(related="pos_config_id.sh_session_wise_option", readonly=False)
    pos_sh_day_wise_option = fields.Selection(related="pos_config_id.sh_day_wise_option", readonly=False)
    pos_sh_last_no_days = fields.Integer(related="pos_config_id.sh_last_no_days", readonly=False)
    pos_sh_last_no_session = fields.Integer(related="pos_config_id.sh_last_no_session", readonly=False)
    pos_sh_how_many_order_per_page = fields.Integer(related="pos_config_id.sh_how_many_order_per_page", readonly=False)

   
    

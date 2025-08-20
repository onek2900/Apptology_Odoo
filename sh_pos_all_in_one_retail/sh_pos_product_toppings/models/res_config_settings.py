from odoo import models, fields, api

class ResConfigSettiongsInhert(models.TransientModel):
    _inherit = "res.config.settings"

    pos_sh_enable_toppings= fields.Boolean(
        related="pos_config_id.sh_enable_toppings", readonly=False)
    pos_sh_add_toppings_on_click_product= fields.Boolean(
        related="pos_config_id.sh_add_toppings_on_click_product", readonly=False)
    pos_sh_allow_same_product_different_qty= fields.Boolean(
        related="pos_config_id.sh_allow_same_product_different_qty", readonly=False)
        
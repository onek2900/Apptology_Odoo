# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.
from odoo import fields, models, api


class ShKeyboardKey(models.Model):
    _name = "sh.keyboard.key"
    _description = "keyboard Key"

    name = fields.Char(string="Key")


class ShKeyboardKeyTemp(models.Model):
    _name = "sh.keyboard.key.temp"
    _description = "keyboard Key Temp"

    sh_key_ids = fields.Many2one("sh.keyboard.key", string="Keys ")
    name = fields.Char(string="Display Key")
    sh_pos_key_ids = fields.Many2one("sh.pos.keyboard.shortcut", string="Keys")

    @api.model_create_multi
    def create(self, vals):
        res = super().create(vals)
        name = ""
        if res.sh_key_ids:
            for each_key in res.sh_key_ids:
                if name != "":
                    name = name + "+" + each_key.name
                else:
                    name = each_key.name
        res.write({"name": name})

        return res


class ShPosKeyboardShortcut(models.Model):
    _name = "sh.pos.keyboard.shortcut"
    _description = "keyboard Key Shortcut"

    payment_config_id = fields.Many2one("pos.config")
    config_id = fields.Many2one("pos.config")
    payment_method_id = fields.Many2one("pos.payment.method")
    sh_key_ids = fields.One2many(
        "sh.keyboard.key.temp", "sh_pos_key_ids", string="Keys"
    )
    sh_payment_shortcut_screen_type = fields.Selection(
        [("payment_screen", "Payment Screen")],
        string="Shortcut Screen Type",
        default="payment_screen",
    )
    sh_shortcut_screen_type = fields.Selection(
        [
            ("payment_screen", "Payment Screen"),
            ("product_screen", "Product Screen"),
            ("customer_screen", "Customer Screen"),
            ("receipt_screen", "Receipt Screen"),
            ("order_screen", "Order Screen"),
            ("all", "All"),
        ],
        string="Shortcut Screen Type ",
    )
    sh_shortcut_screen = fields.Selection(
        [
            ("go_payment_screen", "Go to Payment Screen"),
            ("go_customer_Screen", "Go to Customer Screen"),
            ("go_order_Screen", "Go to Order Screen"),
            ("validate_order", "Validate Order"),
            ("next_order", "Next Order"),
            ("go_to_previous_screen", "Go to Previous Screen"),
            ("select_quantity_mode", "Select Quantity Mode"),
            ("select_discount_mode", "Select Discount Mode"),
            ("select_price_mode", "Select Price Mode"),
            ("search_product", "Search Product"),
            ("search_order", "Search Order"),
            ("add_new_order", "Add New Order"),
            ("destroy_current_order", "Destroy Order"),
            ("delete_orderline", "Delete OrderLine"),
            ("select_up_orderline", "Select Up OrderLine"),
            ("select_down_orderline", "Select Down OrderLine"),
            ("search_customer", "Search Customer"),
            ("select_up_customer", "Select Up Customer"),
            ("select_down_customer", "Select Down Customer"),
            ("set_customer", "Set Customer"),
            ("edit_customer", "Edit Customer"),
            ("save_customer", "Save Customer"),
            ("create_customer", "Create Customer"),
            ("delete_payment_line", "Delete Payment Line"),
            ("select_up_payment_line", "Select Up Payment Line"),
            ("select_down_payment_line", "Select Down Payment Line"),
            ("+10", "+10"),
            ("+20", "+20"),
            ("+50", "+50"),
            ("select_down_order", "Select Down Order"),
            ("select_up_order", "Select Up Order"),
            ("select_order", "Select Order"),
        ],
        string="Shortcut Screen",
    )

# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.
from odoo import fields, models, api


class PosConfig(models.Model):
    _inherit = "pos.config"

    sh_enable_shortcut = fields.Boolean(string="Enable Shortcut Key")
    sh_shortcut_keys_screen = fields.One2many(
        "sh.pos.keyboard.shortcut", "config_id", string="POS Shortcut Key"
    )
    sh_payment_shortcut_keys_screen = fields.One2many(
        "sh.pos.keyboard.shortcut",
        "payment_config_id",
        string="POS Payment Method Shortcut Key",
    )

    @api.model
    def sh_add_default_data(self):
        key_list = []
        vals = []
        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_shift")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_P")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "go_payment_screen",
                    "sh_shortcut_screen_type": "payment_screen",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_control")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_c")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "go_customer_Screen",
                    "sh_shortcut_screen_type": "all",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )

        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_shift")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_G")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "go_order_Screen",
                    "sh_shortcut_screen_type": "product_screen",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_v")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "validate_order",
                    "sh_shortcut_screen_type": "payment_screen",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_n")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "next_order",
                    "sh_shortcut_screen_type": "receipt_screen",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_escape")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "go_to_previous_screen",
                    "sh_shortcut_screen_type": "all",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_q")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "select_quantity_mode",
                    "sh_shortcut_screen_type": "product_screen",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_d")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "select_discount_mode",
                    "sh_shortcut_screen_type": "product_screen",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_p")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "select_price_mode",
                    "sh_shortcut_screen_type": "product_screen",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_f")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "search_product",
                    "sh_shortcut_screen_type": "product_screen",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_f")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "search_order",
                    "sh_shortcut_screen_type": "order_screen",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_Insert")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "add_new_order",
                    "sh_shortcut_screen_type": "all",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_control")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_delete")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "destroy_current_order",
                    "sh_shortcut_screen_type": "all",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_delete")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "delete_orderline",
                    "sh_shortcut_screen_type": "product_screen",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_arrow_up")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "select_up_orderline",
                    "sh_shortcut_screen_type": "product_screen",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_arrow_down")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "select_down_orderline",
                    "sh_shortcut_screen_type": "product_screen",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_f")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "search_customer",
                    "sh_shortcut_screen_type": "customer_screen",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_arrow_up")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "select_up_customer",
                    "sh_shortcut_screen_type": "customer_screen",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_arrow_down")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "select_down_customer",
                    "sh_shortcut_screen_type": "customer_screen",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_Enter")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "set_customer",
                    "sh_shortcut_screen_type": "customer_screen",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_e")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "edit_customer",
                    "sh_shortcut_screen_type": "customer_screen",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_s")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "save_customer",
                    "sh_shortcut_screen_type": "customer_screen",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_+")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "create_customer",
                    "sh_shortcut_screen_type": "customer_screen",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_shift")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_delete")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "delete_payment_line",
                    "sh_shortcut_screen_type": "payment_screen",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_arrow_up")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "select_up_payment_line",
                    "sh_shortcut_screen_type": "payment_screen",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_arrow_down")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "select_down_payment_line",
                    "sh_shortcut_screen_type": "payment_screen",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_F10")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "+10",
                    "sh_shortcut_screen_type": "payment_screen",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_F2")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "+20",
                    "sh_shortcut_screen_type": "payment_screen",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_F5")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "+50",
                    "sh_shortcut_screen_type": "payment_screen",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_arrow_up")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "select_up_order",
                    "sh_shortcut_screen_type": "order_screen",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_arrow_down")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "select_down_order",
                    "sh_shortcut_screen_type": "order_screen",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_Enter")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "select_order",
                    "sh_shortcut_screen_type": "order_screen",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )

        pos_configs = self.env["pos.config"].search(
            [("sh_shortcut_keys_screen", "=", False)]
        )

        key_list = []
        vals = []

        pos_configs.write({"sh_shortcut_keys_screen": vals})
        pos_configs = self.env["pos.config"].search(
            [("sh_payment_shortcut_keys_screen", "=", False)]
        )
        payment_method = self.env["pos.payment.method"].search([])
        if payment_method and len(payment_method) > 0:
            for each_payment_method in payment_method:
                name = each_payment_method.name[0]
                key_id = self.env["sh.keyboard.key"].search([("name", "=", name)])
                temp_key_id = (
                    self.env["sh.keyboard.key.temp"]
                    .sudo()
                    .create({"sh_key_ids": key_id.id})
                )
                key_list.append(temp_key_id.id)
                vals.append(
                    (
                        0,
                        0,
                        {
                            "payment_method_id": each_payment_method.id,
                            "sh_payment_shortcut_screen_type": "payment_screen",
                            "sh_key_ids": [(6, 0, key_list)],
                        },
                    )
                )
                key_list = []
        pos_configs.write({"sh_payment_shortcut_keys_screen": vals})

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        key_list = []
        vals = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_shift")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_P")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "go_payment_screen",
                    "sh_shortcut_screen_type": "payment_screen",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_control")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_c")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "go_customer_Screen",
                    "sh_shortcut_screen_type": "all",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_shift")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_G")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "go_order_Screen",
                    "sh_shortcut_screen_type": "product_screen",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_v")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "validate_order",
                    "sh_shortcut_screen_type": "payment_screen",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_n")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "next_order",
                    "sh_shortcut_screen_type": "receipt_screen",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_escape")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "go_to_previous_screen",
                    "sh_shortcut_screen_type": "all",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_q")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "select_quantity_mode",
                    "sh_shortcut_screen_type": "product_screen",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_d")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "select_discount_mode",
                    "sh_shortcut_screen_type": "product_screen",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_p")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "select_price_mode",
                    "sh_shortcut_screen_type": "product_screen",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_f")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "search_product",
                    "sh_shortcut_screen_type": "product_screen",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_f")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "search_order",
                    "sh_shortcut_screen_type": "order_screen",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_Insert")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "add_new_order",
                    "sh_shortcut_screen_type": "all",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_control")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_delete")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "destroy_current_order",
                    "sh_shortcut_screen_type": "all",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_delete")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "delete_orderline",
                    "sh_shortcut_screen_type": "product_screen",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_arrow_up")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "select_up_orderline",
                    "sh_shortcut_screen_type": "product_screen",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_arrow_down")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "select_down_orderline",
                    "sh_shortcut_screen_type": "product_screen",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_f")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "search_customer",
                    "sh_shortcut_screen_type": "customer_screen",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_arrow_up")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "select_up_customer",
                    "sh_shortcut_screen_type": "customer_screen",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_arrow_down")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "select_down_customer",
                    "sh_shortcut_screen_type": "customer_screen",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_Enter")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "set_customer",
                    "sh_shortcut_screen_type": "customer_screen",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_e")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "edit_customer",
                    "sh_shortcut_screen_type": "customer_screen",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_s")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "save_customer",
                    "sh_shortcut_screen_type": "customer_screen",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_+")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "create_customer",
                    "sh_shortcut_screen_type": "customer_screen",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_shift")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_delete")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "delete_payment_line",
                    "sh_shortcut_screen_type": "payment_screen",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_arrow_up")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "select_up_payment_line",
                    "sh_shortcut_screen_type": "payment_screen",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_arrow_down")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "select_down_payment_line",
                    "sh_shortcut_screen_type": "payment_screen",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_F10")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "+10",
                    "sh_shortcut_screen_type": "payment_screen",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_F2")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "+20",
                    "sh_shortcut_screen_type": "payment_screen",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_F5")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "+50",
                    "sh_shortcut_screen_type": "payment_screen",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_arrow_up")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "select_up_order",
                    "sh_shortcut_screen_type": "order_screen",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_arrow_down")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "select_down_order",
                    "sh_shortcut_screen_type": "order_screen",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        key_id = self.env.ref("sh_pos_all_in_one_retail.sh_keyboard_key_Enter")
        temp_key_id = (
            self.env["sh.keyboard.key.temp"].sudo().create({"sh_key_ids": key_id.id})
        )
        key_list.append(temp_key_id.id)
        vals.append(
            (
                0,
                0,
                {
                    "sh_shortcut_screen": "select_order",
                    "sh_shortcut_screen_type": "order_screen",
                    "sh_key_ids": [(6, 0, key_list)],
                },
            )
        )
        key_list = []

        res.update({"sh_shortcut_keys_screen": vals})
        vals = []
        payment_method = self.env["pos.payment.method"].search([])
        if payment_method and len(payment_method) > 0:
            for each_payment_method in payment_method:
                name = each_payment_method.name[0]
                key_id = self.env["sh.keyboard.key"].search([("name", "=", name)])
                temp_key_id = (
                    self.env["sh.keyboard.key.temp"]
                    .sudo()
                    .create({"sh_key_ids": key_id.id})
                )
                key_list.append(temp_key_id.id)
                vals.append(
                    (
                        0,
                        0,
                        {
                            "payment_method_id": each_payment_method.id,
                            "sh_payment_shortcut_screen_type": "payment_screen",
                            "sh_key_ids": [(6, 0, key_list)],
                        },
                    )
                )
                key_list = []

        res.update({"sh_payment_shortcut_keys_screen": vals})

        return res

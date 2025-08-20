/** @odoo-module */

import {Orderline , Order} from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";
import { ConfirmPopup } from "@point_of_sale/app/utils/confirm_popup/confirm_popup";

patch(Order.prototype, {
    async shRemoveOrderline(line) {
        event.stopPropagation()
            this.removeOrderline(line);
       
    }
});

patch(Orderline.prototype, {
    getDisplayData() {
        let line =  super.getDisplayData()
        line["sh_line"] = this;
        return line
    },
    set_quantity(quantity, keep_price) {
        let res = super.set_quantity(...arguments);
        let self = this
        if (this.pos && this.pos.pos_theme_settings_data && this.pos.pos_theme_settings_data[0].display_product_cart_qty) {
            let orderlines = Object.values(this.order.get_orderlines())
            let other_line_with_same_product = orderlines.filter((x) => (x.product.id == self.product.id && x != self))

            if (other_line_with_same_product.length > 0) {
                let total_qty = 0
                other_line_with_same_product.map((x) => total_qty += x.quantity)
                total_qty += self.quantity
                if (this.order.product_with_qty) {
                    this.order.product_with_qty[this.product.id] = total_qty != 0 ? total_qty : false;
                } else {
                    this.order.product_with_qty = {}
                    this.order.product_with_qty[this.product.id] = total_qty != 0 ? total_qty : false;
                }
                this.order['product_with_qty']
            } else {
                if (this.order.product_with_qty) {
                    this.order.product_with_qty[this.product.id] = this.quantity != 0 ? this.quantity : false
                } else {
                    this.order.product_with_qty = {};
                    this.order.product_with_qty[this.product.id] = this.quantity != 0 ? this.quantity : false
                }
            }
        }
        return res
    },
    getDisplayData() {
        let res = super.getDisplayData();
        res['product_id'] = this.get_product().id
        res['write_date'] = this.get_product().write_date
        return res
    }
});

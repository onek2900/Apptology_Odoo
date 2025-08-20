/* @odoo-modules */

import { Orderline, Order } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";
import { DiscountPopupWidget } from "@sh_pos_all_in_one_retail/static/sh_pos_discount/app/popup/discount_popup/discount_popup";

patch(Order.prototype, {
    setup(_defaultObj, options){
        super.setup(...arguments)
    },
    async on_click_show_discount() {
        var self = this;
        if(Object.keys(self.pos.all_discount).length){
            let { confirmed, payload } = this.env.services.popup.add(DiscountPopupWidget);
            if (confirmed) {
            } else {
                return;
            }
        }else{
            alert("System not found any custom discount.")
        }
    }
})

patch(Orderline.prototype, {
    setup(_defaultObj, options) {
        super.setup(...arguments);
        if (options && options.json && (options.json.line_discount || options.json.line_discount_code)) {
            this.line_discount = options.json.line_discount;
            this.line_discount_code = options.json.line_discount_code;
        } else {
            this.line_discount = "";
            this.line_discount_code = "";
        }
    },
    set_line_discount(line_discount) {
        this.line_discount = line_discount
    },
    get_line_discount() {
        if(this.get_discount()){
            return this.line_discount;
        }else{
            return false
        }
    },
    set_line_discount_code(line_discount_code) {
        this.line_discount_code = line_discount_code;
        if (line_discount_code && line_discount_code.length == 1) {
            this.display_line_discount_code = line_discount_code[0];
        } else {
            var display_code_string = "";
            for (var i = 0; i < line_discount_code.length; i++) {
                if (i == line_discount_code.length - 1) {
                    display_code_string = display_code_string + line_discount_code[i];
                } else {
                    display_code_string = display_code_string + line_discount_code[i] + " , ";
                }
            }
            this.line_discount_code = display_code_string
        }
    },
    get_line_discount_code() {
        if(this.get_discount()){
            return this.line_discount_code;
        }else{
            return false
        }
    },
    export_as_JSON() {
        var json = super.export_as_JSON(arguments);
        json.line_discount = this.line_discount || null;
        json.sh_discount_code = this.get_line_discount().toString() || null;
        return json;
    },
    getDisplayData() {
        let lines = super.getDisplayData()
        // var self = this;
        // var new_attr = {
        //     line_discount: this.get_line_discount() || false,
        // };
        lines["get_line_discount"] = this.get_line_discount()
        // $.extend(lines, new_attr);
        return lines;
    
    },
    async on_click_show_discount(event) {
        var self = this;
        let { confirmed, payload } = self.showPopup("DiscountPopupWidget");
        if (confirmed) {
        } else {
            return;
        }
    }
});

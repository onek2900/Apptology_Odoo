/** @odoo-module */

import {  Orderline, Order } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";


patch(Orderline.prototype, {
    init_from_JSON (json) {
        super.init_from_JSON(...arguments);
        if (json && json.line_note){
            this.line_note = json.line_note || ""
        }
    },
    set_line_note (line_note) {
        this.line_note = line_note;
    },
    get_line_note  () {
        return this.line_note;
    },

    getDisplayData() {
        var lines = super.getDisplayData(...arguments);
        lines['line_note'] = this.get_line_note() || false
        lines['show_icon'] = this.order && !this.order.finalized  || false
        return lines
    },
    export_as_JSON () {
        const json = super.export_as_JSON(...arguments);
        json.line_note = this.get_line_note() || null;
        return json;
    } 
    
});



patch(Order.prototype, {
    init_from_JSON (json) {
        super.init_from_JSON(...arguments);
        if (json && json.order_note){
            this.order_note = json.order_note || ""
        }
    },
    set_global_note (order_note) {
        this.order_note = order_note;
    },
    get_global_note  () {
        return this.order_note;
    },
    export_as_JSON () {
        const json = super.export_as_JSON(...arguments);
        json.order_note = this.get_global_note() || null;
        return json;
    },
    export_for_printing() {
        var self = this;
        var orders = super.export_for_printing(...arguments);
        orders['order_global_note'] = self.get_global_note() || false
        return orders
    }
})
/** @odoo-module */

import { Order } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";

patch(Order.prototype, {
    init_from_JSON(json) {
        super.init_from_JSON(...arguments);
        this.signature_date = json.signature_date ||  ""
        this.signature_name = json.signature_name ||  ""
        this.signature = json.signature ||  ""
    },
    set_signature_date(signature_date) {
        this.assert_editable();
        this.signature_date = signature_date  
    },
    get_signature_date() {
        return this.signature_date || false;
    },
    set_signature_name(signature_name) {
        this.assert_editable();
        this.signature_name = signature_name  
    },
    get_signature_name() {
        return this.signature_name || false;
    },
    set_signature(signature) {
        this.assert_editable();
        this.signature = signature  
    },
    get_signature() {
        return this.signature || false;
    },
    export_as_JSON() {
        var json = super.export_as_JSON(...arguments);
        // var new_val = {
        json.signature = this.get_signature() || "";
        json.signature_name = this.get_signature_name() || "";
        json.signature_date = this.get_signature_date() || "";
        // };
        // $.extend(submitted_order, new_val);
        return json;
    },
    export_for_printing() {
        var self = this;
        var orders = super.export_for_printing(...arguments);
        var new_val = {
            signature: this.get_signature(),
            signature_name: this.get_signature_name(),
            signature_date: this.get_signature_date(),
        };
        $.extend(orders, new_val);
        return orders;
    }
});


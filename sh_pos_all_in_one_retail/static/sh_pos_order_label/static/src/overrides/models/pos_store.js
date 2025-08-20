/** @odoo-module */

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { patch } from "@web/core/utils/patch";

patch(PosStore.prototype, {
    async setup(env, { popup, orm, number_buffer, hardware_proxy, barcode_reader, ui }) {
       await super.setup(...arguments)
        this.order_line_product = this.db.get_order_label_product()
    },
    get_orderline_product(){
        return this.order_line_product
    }
});

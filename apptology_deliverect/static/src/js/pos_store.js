/** @odoo-module **/

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { patch } from "@web/core/utils/patch";

patch(PosStore.prototype, {
    async get_online_orders() {
        try {
            var new_orders = await this.orm.call("pos.order", "get_new_orders", []);
            return new_orders
        } catch(error){
            console.error("Error fetching new online orders:",error)
        }
    },
});

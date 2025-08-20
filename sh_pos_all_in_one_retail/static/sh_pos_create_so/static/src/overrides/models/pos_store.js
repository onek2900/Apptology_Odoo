/** @odoo-module */

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { patch } from "@web/core/utils/patch";

patch(PosStore.prototype, {
    async setup(env, { popup, orm, number_buffer, hardware_proxy, barcode_reader, ui }) {
        await super.setup(...arguments)
        this.db.all_sale_orders = []
    },
    async create_sale_order() {
        var self = this;

        var All_SO = self.db.get_all_sale_orders();
        return await this.orm.call("pos.order", "sh_create_sale_order", [All_SO, self.config.select_order_state]);
    }

});


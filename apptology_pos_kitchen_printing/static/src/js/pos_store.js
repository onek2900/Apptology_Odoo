/** @odoo-module */

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { patch } from "@web/core/utils/patch";

patch(PosStore.prototype, {
    async sendOrderInPreparationUpdateLastChange(order, cancelled = false) {
        order.updateLastOrderChange();

        //We make sure that the last_order_change is updated in the backend
        order.save_to_db();
        order.pos.ordersToUpdateSet.add(order);
        await order.pos.sendDraftToServer();
    }
})

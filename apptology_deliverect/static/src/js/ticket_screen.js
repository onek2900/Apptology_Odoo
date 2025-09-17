/** @odoo-module **/

import { TicketScreen } from "@point_of_sale/app/screens/ticket_screen/ticket_screen";
import { patch } from "@web/core/utils/patch";

patch(TicketScreen.prototype, {
    /**
     * Avoid full reloads that duplicate orders in memory.
     * For online orders, prefer a lightweight sync if available.
     */
    async _setOrder(order) {
        if (order && order.name && order.name.includes("Online-Order")) {
            try {
                if (typeof this.pos._syncTableOrdersFromServer === "function") {
                    await this.pos._syncTableOrdersFromServer();
                } else if (typeof this.pos.syncTableOrdersFromServer === "function") {
                    // fallback name in some deployments
                    await this.pos.syncTableOrdersFromServer();
                } else {
                    // Intentionally skip load_server_data() to prevent duplicates
                }
            } catch (e) {
                console.warn("Lightweight POS order sync failed", e);
            }
        }
        return super._setOrder(...arguments)
    }
});

/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { Order } from "@point_of_sale/app/store/models";

patch(Order.prototype, {
    setup() {
        super.setup(...arguments);
    },
    get_screen_data() {
        // Preserve previously saved screen when coming from OnlineOrderScreen to avoid
        // forcing a ProductScreen that can trigger creation of a blank draft order.
        const screen = this.screen_data["value"];
        if (!screen) {
            // No saved screen: route based on payment lines only
            return this.get_paymentlines().length > 0
                ? { name: "PaymentScreen" }
                : { name: "ProductScreen" };
        }
        if (screen?.name === 'OnlineOrderScreen') {
            // Keep current context; do not force ProductScreen
            return this.get_paymentlines().length > 0
                ? { name: "PaymentScreen" }
                : (this.finalized ? { name: "TicketScreen" } : { name: "ProductScreen" });
        }
        if (!this.finalized && this.get_paymentlines().length > 0) {
            return { name: "PaymentScreen" };
        }
        return screen;
    }
});

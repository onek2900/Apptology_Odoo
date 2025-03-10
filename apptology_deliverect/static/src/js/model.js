/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { Order } from "@point_of_sale/app/store/models";

patch(Order.prototype, {
    setup() {
        super.setup(...arguments);
    },
    get_screen_data() {
//    function modified to consider switching from online order screen
        const screen = this.screen_data["value"];
        // If no screen data is saved
        //   no payment line -> product screen
        //   with payment line -> payment screen
        if (!screen || screen?.name=='OnlineOrderScreen') {
            if (this.get_paymentlines().length > 0) {
                return { name: "PaymentScreen" };
            }
            return { name: "ProductScreen" };
        }
        if (!this.finalized && this.get_paymentlines().length > 0) {
            return { name: "PaymentScreen" };
        }
        return screen;
    }
});
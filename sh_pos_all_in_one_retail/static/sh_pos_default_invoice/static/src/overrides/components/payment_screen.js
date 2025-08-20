/** @odoo-module */

import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";

patch(PaymentScreen.prototype, {
    setup() {
        super.setup();
        if (this.pos.config.sh_enable_default_invoice) {
            this.currentOrder.set_to_invoice(true)
        }
    },
});

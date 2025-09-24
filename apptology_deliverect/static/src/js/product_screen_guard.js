/** @odoo-module */

import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { patch } from "@web/core/utils/patch";

patch(ProductScreen.prototype, {
    setup() {
        super.setup(...arguments);
        // Ensure a current order exists to avoid null deref in core setup
        try {
            if (!this.pos.get_order()) {
                this.pos.add_new_order();
            }
        } catch (e) {
            console.warn("ProductScreen guard: unable to ensure a current order", e);
        }
    },
});


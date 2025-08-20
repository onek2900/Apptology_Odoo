/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { patch } from "@web/core/utils/patch";

patch(ProductScreen.prototype, {
    setup() {
        super.setup(...arguments);
    },
    _setValue(val) {
        super._setValue(val)
        if (this.currentOrder.get_selected_orderline()) {
            if (this.pos.numpadMode === "price") {
                var selected_orderline = this.currentOrder.get_selected_orderline();
                selected_orderline.is_added = true;
                selected_orderline.price_manually_set = true;
            }
        }
    }
});

/** @odoo-module */

import { ClosePosPopup } from "@point_of_sale/app/navbar/closing_popup/closing_popup";
import { patch } from "@web/core/utils/patch";
import { ProductDetailsPopup } from "@pos_product_detail/component/product_details_popup/product_details_popup";

patch(ClosePosPopup.prototype, {
    async showProductDetails() {
        const posSessionId = this.pos.pos_session.id;
        const data = await this.orm.call("pos.session", "get_session_products", [posSessionId]);
        this.popup.add(ProductDetailsPopup, {
            title: "Session Products",
            size: 'medium',
            products: data,
        });
    }
});
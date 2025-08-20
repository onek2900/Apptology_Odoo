/** @odoo-module */

import { Orderline } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";


patch(Orderline.prototype, {
    getDisplayData() {
        var res = super.getDisplayData()
        res['product_type'] = this.get_product().type
        res['productId'] = this.get_product().id
        return res
    }     
});

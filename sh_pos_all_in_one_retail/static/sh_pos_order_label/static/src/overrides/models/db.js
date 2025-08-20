/** @odoo-module */

import { PosDB } from "@point_of_sale/app/store/db";
import { patch } from "@web/core/utils/patch";

patch(PosDB.prototype, {
    get_order_label_product() {
        var products = this.product_by_id
        products =  Object.values(products)
        var product1 = {}
        for(let product of products){
            if(product.sh_order_label_demo_product) {
                product1 = product
            }
        }
        return product1
    }
})
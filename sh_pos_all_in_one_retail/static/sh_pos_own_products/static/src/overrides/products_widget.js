/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { ProductsWidget } from "@point_of_sale/app/screens/product_screen/product_list/product_list";

patch(ProductsWidget.prototype,{
    // get productsToDisplay() {
    //     var self = this
    //     var products = super.productsToDisplay
    //     var product_list = []
    //     if (self.pos.config.sh_enable_own_product) {
    //         if (self.pos.user.role != 'manager') {
    //             for (var i = 0; i < products.length; i++) {
    //                 var product = products[i]
    //                 if (product.sh_select_user.includes(self.pos.user.id)) {
    //                     product_list.push(product)
    //                 }
    //             }
    //         } else {
    //             return products
    //         }
    //         if (product_list.length > 0) {
    //             return product_list
    //         } else {
    //             return []
    //         }
    //     } else {
    //         return products
    //     }
    // }
});

/** @odoo-module */

import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { patch } from "@web/core/utils/patch";
import { ToppingsPopup } from "@sh_pos_all_in_one_retail/static/sh_pos_product_toppings/app/Popups/ToppingsPopup/ToppingsPopup";
import { useService } from "@web/core/utils/hooks";

patch(ProductScreen.prototype, {
    async selectLine(orderline) {
        await super.selectLine(orderline)
        var self = this;
            const product = orderline.get_product()
            var category;
            var product_ids = []
            var Topping_products = []

            if (product.pos_categ_ids && product.pos_categ_ids[0]) {
                category = self.pos.db.get_category_by_id(product.pos_categ_ids[0])
            }

            if (category && category.sh_product_topping_ids) {
                category.sh_product_topping_ids.forEach(function (product_id) {
                    if(self.pos.db.product_by_id[product_id]){
                        Topping_products.push(self.pos.db.product_by_id[product_id])
                        product_ids.push(product_id)
                    }
                });
            }
            await product.sh_topping_ids.forEach(function (each_id) {
                if (!product_ids.includes(each_id)) {
                    if(self.pos.db.product_by_id[each_id]){
                        Topping_products.push(self.pos.db.product_by_id[each_id])
                    }
                }
            });

            var allproducts = []
            if (!self.isMobile && $('.search-box input') && $('.search-box input').val() != "") {
                allproducts = this.pos.db.search_product_in_category(
                    self.pos.selectedCategoryId,
                    $('.search-box input').val()
                );
            } else {
                allproducts = self.pos.db.get_product_by_category(0);
            }


            if (self.pos.config.sh_enable_toppings) {
                if (Topping_products.length > 0) {
                    let { confirmed } = await  this.popup.add(ToppingsPopup, {'title' : 'Toppings','Topping_products': Topping_products, 'Globaltoppings': []});
                    if (confirmed) {
                    } else {
                        return;
                    }
                }
            }
    },
    setup() {
        super.setup()
        this.popup = useService("popup");
    },
    // async _clickRemoveLine({ detail: line_id }) {
    //     var self = this;
        
    //     setTimeout(async () => {
    //         var order = self.env.pos.get_order()
    //         var line = this.env.pos.get_order().get_orderline(line_id)
    //         if (order && order.get_selected_orderline() && order.get_selected_orderline().Toppings) {

    //             var data = await $.grep(order.get_selected_orderline().Toppings, function (topping) {
    //                 return topping.id != line_id;
    //             });

    //             var data1 = await $.grep(order.get_selected_orderline().Toppings_temp, function (topping1) {
    //                 return topping1.id != line_id;
    //             });

    //             order.get_selected_orderline().Toppings = data
    //             order.get_selected_orderline().Toppings_temp = data1

    //             self.pos.get_order().removeOrderline(line)
    //         }
    //     }, 100);
    // },
});

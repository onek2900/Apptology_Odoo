/** @odoo-module */
import { patch } from "@web/core/utils/patch";
import { Orderline } from "@point_of_sale/app/store/models";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import {
    formatFloat,
    roundDecimals as round_di,
    roundPrecision as round_pr,
    floatIsZero,
} from "@web/core/utils/numbers";

import { parseFloat as oParseFloat } from "@web/views/fields/parsers";

patch(Orderline.prototype, {
    setup(){
        super.setup(...arguments)
        this.is_added = true
    },
    set_unit_price(price) {
        var self = this;
        this.min_price_pricelist;
        var line = this.pos.get_order() ? this.pos.get_order().get_selected_orderline(): false;

        // if (!line) {
        //     this.pos.get_order().select_orderline(this);
        // }
        // if (this.pos.get_all_pricelist() && line) {
        //     for(let each_pricelist of this.pos.get_all_pricelist()){
        //         if (each_pricelist.id == self.pos.config.sh_min_pricelist_value[0]) {
        //             var price;
        //             each_pricelist["items"] = [];
        //             for(let each_item of each_pricelist.item_ids){
        //                 var item_data = self.pos.db.pricelist_item_by_id[each_item];
        //                 if (item_data.product_tmpl_id[0] == line.product.product_tmpl_id) {
        //                     each_pricelist["items"].push(item_data);
        //                     each_pricelist["product_tml_id"] = line.product.product_tmpl_id;
        //                     price = line.product.get_price(each_pricelist, line.get_quantity());
        //                     each_pricelist["display_price"] = price;
        //                     self.min_price_pricelist = each_pricelist;
        //                 }
        //                 if (item_data.display_name == "All Products") {
        //                     each_pricelist["items"].push(item_data);
        //                     each_pricelist["product_tml_id"] = "All Products";
        //                     price = line.product.get_price(each_pricelist, line.get_quantity());
        //                     each_pricelist["display_price"] = price;
        //                     self.min_price_pricelist = each_pricelist;
        //                 }
        //             };
        //         }
        //     };
        // }
        if (self.min_price_pricelist && self.min_price_pricelist.display_price) {
            if (self.min_price_pricelist.product_tml_id && self.min_price_pricelist.product_tml_id == "All Products" && price < self.min_price_pricelist.display_price && self.is_added) {
                this.pos.env.services.popup.add(ErrorPopup, {
                    title: 'Price Warning ',
                    body: 'MINIMUM',
                });
               
                self.is_added = false;
            } else if (self.min_price_pricelist.product_tml_id && self.min_price_pricelist.product_tml_id == line.product.product_tmpl_id && price < self.min_price_pricelist.display_price && self.is_added) {
                this.pos.env.services.popup.add(ErrorPopup, {
                    title: 'Price Warning ',
                    body: 'PRICE IS BELOW MINIMUM',
                });

                self.is_added = false;
            } else {
                this.order.assert_editable();

                var parsed_price = !isNaN(price)
                    ? price
                    : isNaN(parseFloat(price))
                    ? 0
                    : oParseFloat("" + price);
                this.price = round_di(parsed_price || 0, this.pos.dp["Product Price"]);
            }
        } else {
            this.order.assert_editable();
            var parsed_price = !isNaN(price)
                    ? price
                    : isNaN(parseFloat(price))
                    ? 0
                    : oParseFloat("" + price);
            this.price = round_di(parsed_price || 0, this.pos.dp["Product Price"]);
        }
    },
    set_pricelist(pricelist) {
        this.pricelist = pricelist;
    },
    get_pricelist() {
        return this.pricelist || false;
    },
});

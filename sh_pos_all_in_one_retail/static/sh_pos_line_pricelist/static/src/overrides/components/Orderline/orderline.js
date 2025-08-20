/* @odoo-modules */

import { Orderline, Order } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";
import { PriceListPopupWidget } from "@sh_pos_all_in_one_retail/static/sh_pos_line_pricelist/apps/pricelist_popup/pricelist_popup";

patch(Order.prototype, {
    async on_click_pricelist_icon(line) {
        var self = line;
        debugger;
        line.available_pricelist = [];
        line.pricelist_for_code = [];
        line.min_price_pricelist;
            for (var k = 0; k < self.pos.get_all_pricelist().length; k++) {
                var each_pricelist = self.pos.get_all_pricelist()[k]
                if (each_pricelist.id == self.pos.config.sh_min_pricelist_value[0]) {
                    var price;
                    each_pricelist["items"] = [];
                    for (var i = 0; i < each_pricelist.item_ids.length; i++) {
                        var each_item = each_pricelist.item_ids[i]
                        var item_data = self.pos.db.pricelist_item_by_id[each_item];
                        if (item_data.product_tmpl_id[0] == line.product.product_tmpl_id) {
                            each_pricelist["items"].push(item_data);
                            each_pricelist["product_tml_id"] = line.product.product_tmpl_id;
                        }
                        if (item_data.display_name == "All Products") {
                            each_pricelist["items"].push(item_data);
                            each_pricelist["product_tml_id"] = "All Products";
                        }
                    }

                    price = line.product.get_price(each_pricelist, line.get_quantity());
                    each_pricelist["display_price"] = price;
                    self.min_price_pricelist = each_pricelist;
                }
                if (each_pricelist.id == self.pos.config.sh_pricelist_for_code[0]) {
                    var price;
                    each_pricelist["items"] = [];
                    for (var j = 0; j < each_pricelist.item_ids.length; j++) {
                        var each_item = each_pricelist.item_ids[j]
                        var item_data = self.pos.db.pricelist_item_by_id[each_item];
                        each_pricelist["items"].push(item_data);
                    }
                    
                    price = line.product.get_price(each_pricelist, line.get_quantity());
                    var sNumber = price.toString();
                    var code = "";
                    for(var each_number of sNumber){
                        if (each_number == "1") {
                            code += "L";
                        }
                        if (each_number == "2") {
                            code += "U";
                        }
                        if (each_number == "3") {
                            code += "C";
                        }
                        if (each_number == "4") {
                            code += "K";
                        }
                        if (each_number == "5") {
                            code += "Y";
                        }
                        if (each_number == "6") {
                            code += "H";
                        }
                        if (each_number == "7") {
                            code += "O";
                        }
                        if (each_number == "8") {
                            code += "R";
                        }
                        if (each_number == "9") {
                            code += "S";
                        }
                        if (each_number == "0") {
                            code += "E";
                        }
                        if (each_number == ".") {
                            code += ".";
                        }
                    };
                    each_pricelist["display_price"] = code;
                    self.pricelist_for_code.push(each_pricelist);
                } else {
                    if (self.pos.config.available_pricelist_ids.includes(each_pricelist.id)) {
                        var price;
                        each_pricelist["items"] = [];
                        for (var j = 0; j < each_pricelist.item_ids.length; j++) {
                            var each_item = each_pricelist.item_ids[j];
                            var item_data = self.pos.db.pricelist_item_by_id[each_item];
                            each_pricelist["items"].push(item_data);
                        }

                        price = await line.product.get_price(each_pricelist, line.get_quantity());
                        each_pricelist["display_price"] = price;
                        self.available_pricelist.push(each_pricelist);
                    }
                }
            }
            this.env.services.popup.add(PriceListPopupWidget, {
                'available_pricelist': self.available_pricelist,
                'pricelist_for_code': self.pricelist_for_code,
                'min_price_pricelist': self.min_price_pricelist,
            });
    }
 })
patch(Orderline.prototype, {
    getDisplayData() {
        return {
            ...super.getDisplayData(),
            sh_model_line: this
        }
    },
});

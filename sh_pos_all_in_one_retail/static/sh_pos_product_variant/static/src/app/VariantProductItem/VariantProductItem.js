/** @odoo-module */

import { Component } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";

export class VariantProductItem extends Component {
    static template = "sh_pos_all_in_one_retail.VariantProductItem";

    setup() {
        this.pos = usePos();
    }
    get get_display_stock() {
        var product_id = this.props.productId
        var location_id = this.env.services.pos.config.sh_pos_location ? this.env.services.pos.config.sh_pos_location[0] : false
        var stocks = this.env.services.pos.db.get_stock_by_product_id(product_id)
        var qty = 0.00
        if (location_id && stocks && stocks.length) {
            var sh_stock = stocks.filter((stock) => stock.location_id == location_id)
            if (sh_stock && sh_stock.length) {
                qty = sh_stock[0].quantity
            }
        }
        return qty
    }
}

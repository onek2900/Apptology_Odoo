/** @odoo-module */

import { Order } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";

patch(Order.prototype, {
    export_for_printing() {
        var orders = super.export_for_printing(...arguments);
        orders['total_items'] = false 
        orders['total_qty'] = this.get_total_qty() || false
        
        if (this.get_orderlines()){
            var lines = this.get_orderlines().filter((line) => !line.is_topping)
            orders['total_items'] = lines.length
        }
        return orders
    },
    get_total_qty() {
        let qty = 0 
        for(let line of this.get_orderlines()){
            if (!line.is_topping){
                qty += line.get_quantity()
            }
        }
        return qty
    }
});

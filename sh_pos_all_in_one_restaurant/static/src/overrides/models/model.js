/** @odoo-module */

import { Order, Orderline } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";

patch(Orderline.prototype, {
    export_as_JSON() {
        const json = super.export_as_JSON(...arguments);
        
        if (this.is_has_topping){
            json['topping_uuids'] = this.Toppings_temp.map(x =>x.uuid)
        }
        
        return json
    }
})
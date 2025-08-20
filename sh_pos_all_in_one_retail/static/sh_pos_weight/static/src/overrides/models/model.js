/** @odoo-module */

import { Order, Orderline } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";

patch(Order.prototype, {
    get_total_weight () {
    
        var order = this
        
        var total_weight = 0.0
        if (order.get_orderlines()) {
            for(let line of order.get_orderlines()){
                total_weight += line.product.weight * line.quantity
            }
        }
        return total_weight.toFixed('2')
    },
    get_total_volume () {
        var order = this;
        var total_volume = 0.0
        if (order.get_orderlines()) {
            for(let line of order.get_orderlines()){
                total_volume += line.product.volume * line.quantity
            }
        } 
        return total_volume.toFixed('2')
        
    },
    export_for_printing() {
        var orders = super.export_for_printing(...arguments);
        orders['total_product_weight'] = this.get_total_weight() || 0
        orders['total_product_volume'] = this.get_total_volume() || 0.0
        return orders
    },
    export_as_JSON () {
        const json = super.export_as_JSON(...arguments);
        json.total_product_weight = this.get_total_weight() || 0
        json.total_product_volume = this.get_total_volume() || 0.0
        return json;
    },
});

patch(Orderline.prototype, {
    init_from_JSON (json) {
        super.init_from_JSON(...arguments);
        if (json && json.total_product_weight){
            this.total_product_weight = json.total_product_weight || ""
        }
        if (json && json.total_product_volume){
            this.total_product_volume = json.total_product_volume || ""
        }
    },
    export_as_JSON () {
        const json = super.export_as_JSON(...arguments);
        json.product_weight = this.product.weight
        json.product_volume = this.product.volume
        json.total_product_weight = this.product.weight * this.quantity || false
        json.total_product_volume = this.product.volume * this.quantity || false
        return json;
    },
    getDisplayData() {
        return {
            ...super.getDisplayData(),

            weight_in_cart: this.order && !this.order.finalized && this.pos.config.enable_weight,
            weight_in_receipt: this.order && this.order.finalized && this.pos.config.product_weight_receipt,
            volume_in_receipt : this.order && this.order.finalized && this.pos.config.product_volume_receipt,
            volume_in_cart: this.order && !this.order.finalized && this.pos.config.enable_volume,

            product_weight: (parseFloat(this.product.weight) * parseFloat(this.quantity)),
            product_volume: (parseFloat(this.product.volume) * parseFloat(this.quantity)),
        };
    },
    
});

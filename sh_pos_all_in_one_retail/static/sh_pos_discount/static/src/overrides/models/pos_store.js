/** @odoo-module */

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { patch } from "@web/core/utils/patch";

patch(PosStore.prototype, {
    // @Override
    async _processData(loadedData) {
        await super._processData(...arguments);
        this.all_discount = loadedData['sh.pos.discount']
        this.all_discount = Object.values(this.all_discount)
        this.discount_by_id = {}
        for(let i=0; i<= this.all_discount.length ; i++){
            var discount = this.all_discount[i];
            if(discount){
                this.discount_by_id[discount.id] = discount;
            }
        }
    },
});

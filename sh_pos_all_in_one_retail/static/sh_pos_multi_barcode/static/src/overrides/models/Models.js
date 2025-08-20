/** @odoo-module */

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { patch } from "@web/core/utils/patch";

patch(PosStore.prototype, {
    async _processData(loadedData) {
        var self = this
        self.db.multi_barcode_by_id = loadedData['product_by_barcode'] || {}
        await super._processData(...arguments);
        this.db.barcode_search_str = ""
        if (self.db.multi_barcode_by_id){
            for(let i=0; i< Object.values(self.db.multi_barcode_by_id).length; i++){
                let barcode_obj = Object.values(self.db.multi_barcode_by_id)[i]
                self.db.product_by_barcode[barcode_obj.name] = self.db.get_product_by_id(barcode_obj.product_id)
            }            
        }
    }
});

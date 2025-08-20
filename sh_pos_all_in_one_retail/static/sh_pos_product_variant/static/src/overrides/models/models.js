/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";

patch(PosStore.prototype, {
    async _processData(loadedData) {
        // this.db.product_by_tmpl_id = {}
        this.db.alternative_product_by_id = {}
        await super._processData(...arguments)
        this.db.attribute_by_id = loadedData['attribute_by_id'] || []
        this.db.attribute_value_by_id = loadedData['attribute_value_by_id'] || [] 
    }
});

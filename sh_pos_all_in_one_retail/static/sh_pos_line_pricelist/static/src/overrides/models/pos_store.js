/** @odoo-module */
import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";

patch(PosStore.prototype, {
    async _processData(loadedData) {
        super._processData(...arguments)
        this.db.all_pricelists = loadedData['all_pricelists'] || [];
        this.db.pricelist_by_id = loadedData['pricelist_by_id'] || [];
        this.db.all_pricelists_item = loadedData['all_pricelists_item'] || [];
        this.db.pricelist_item_by_id = loadedData['pricelist_item_by_id'] || [];
    },
    get_all_pricelist: function () {
        return this.db.all_pricelists;
    },
});

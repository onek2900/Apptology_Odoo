/** @odoo-module */

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { patch } from "@web/core/utils/patch";

patch(PosStore.prototype, {
    async _processData(loadedData) {
        await super._processData(...arguments);
            this.pre_defined_note_data_dict = loadedData['pre_defined_note_data_dict'] || [];
            this.db.all_note_names = loadedData['all_note_names'] || [];
        
    }
});

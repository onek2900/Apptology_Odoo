/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { _t } from "@web/core/l10n/translation";


patch(PosStore.prototype, {
    async _processData(loadedData) {
        await super._processData(...arguments);
        if(loadedData['pos_order_by_id']){
            this.db.pos_order_by_id = loadedData['pos_order_by_id']
        }else{
            this.db.pos_order_by_id = {}
        }
        if(loadedData['pos_order_line_by_id']){
            this.db.pos_order_line_by_id = loadedData['pos_order_line_by_id']
        }else{
            this.db.pos_order_line_by_id = {}
        }
    },
})
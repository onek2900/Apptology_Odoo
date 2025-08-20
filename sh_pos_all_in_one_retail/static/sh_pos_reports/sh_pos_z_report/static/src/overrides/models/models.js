/** @odoo-module */

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { patch } from "@web/core/utils/patch";

patch(PosStore.prototype, {
  async setup() {
    await super.setup(...arguments);
    this.posted_session_ids = [];
  },
  async _processData(loadedData) {
    await super._processData(...arguments);
    super._processData(loadedData)
    if(loadedData && loadedData['posted_session']){
        this.db.posted_session_ids = loadedData['posted_session'];
    }
  },
});

    /** @odoo-module */

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { patch } from "@web/core/utils/patch";

patch(PosStore.prototype,  {
    async setup(env, { popup, orm, number_buffer, hardware_proxy, barcode_reader, ui }) {
        await super.setup(...arguments)
        this.db.all_purchase_orders = []
    },
      async  create_purchase_order() {
            var self = this;
            var All_PO = self.db.get_all_orders();
            
            return await this.orm.call("pos.order", "sh_create_purchase", [All_PO, self.config.select_purchase_state]);
        
        }
    
});


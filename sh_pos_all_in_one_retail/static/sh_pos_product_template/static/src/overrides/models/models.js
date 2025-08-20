/** @odoo-module */

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { Orderline } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";

patch(PosStore.prototype, {
    async _processData(loadedData) {
        await super._processData(...arguments);
        var self = this
        self.pos_product_templates = loadedData['pos.product.template'] || []
        self.pos_product_template_lines = loadedData['pos.product.template.line']|| []

        self.template_line_by_id = {};
        var data_list = [];

        for(let line of self.pos_product_template_lines){
            if (line.pos_template_id in self.template_line_by_id) {
                var temp_list = self.template_line_by_id[line.pos_template_id];
                temp_list.push(line);
                self.template_line_by_id[line.pos_template_id] = temp_list;
            } else {
                data_list = [];
                data_list.push(line);
                self.template_line_by_id[line.pos_template_id] = data_list;
            }
        };
        
    }
});

patch(Orderline.prototype, {
    set_unit_price(price){
        super.set_unit_price(price)
        if(this && this.is_template_product){
            super.set_unit_price(this.template_price) 
        }
        
    }
});

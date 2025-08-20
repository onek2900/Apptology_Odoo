/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";

patch(PosStore.prototype, {
    //@override
    async _processData(loadedData) {
        await super._processData(...arguments);
        this.pos_theme_settings_data = loadedData['sh.pos.theme.settings'] || [];
        this.pos_theme_settings_data_by_theme_id = loadedData?.pos_theme_settings_data_by_theme_id || []
    },
    get_product_image_url(product_id,write_date){
        return `/web/image?model=product.product&field=image_128&id=${product_id}&write_date=${write_date}&unique=1`;
    },
    async setup(env, { popup, orm, number_buffer, hardware_proxy, barcode_reader, ui }) {
        await super.setup(...arguments);
        if(this.pos_theme_settings_data && this.pos_theme_settings_data[0] && this.pos_theme_settings_data[0].sh_mobile_start_screen && this.pos_theme_settings_data[0].sh_mobile_start_screen == 'cart_screen'){
            this.mobile_pane = "left";
        }
    },
    get cart_item_count(){
        // return 2
        alert()
        if(this.pos_theme_settings_data && this.pos_theme_settings_data[0].display_cart_order_item_count && this.get_order()){
            return this.get_order().get_orderlines().length
        }else{
            return 0
        }
    },
    async removelineClick(line) {
        var self = this;
        console.log("self.get_order()", self.get_order() , line);
        self.get_order().select_orderline(line);
        // this.trigger('select-line', { orderline: line });

        self.get_order().removeOrderline(self.pos.get_order().get_selected_orderline())
        
    }
});

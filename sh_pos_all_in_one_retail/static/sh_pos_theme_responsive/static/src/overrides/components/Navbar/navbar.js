/** @odoo-module */

import { Navbar } from "@point_of_sale/app/navbar/navbar";
import { patch } from "@web/core/utils/patch";
import { onMounted } from "@odoo/owl";

patch(Navbar.prototype, {
    setup() {
        super.setup();
        onMounted(this.onMounted);
        if(this.pos.get_order()){
            this.pos.get_order().is_reciptScreen =  false;
        }
    },
    onMounted() {
        var self = this
        setTimeout(() => {
            if (localStorage.getItem("sh_pos_night_mode") == 'true') {
                $(".pos").addClass("sh_pos_night_mode")
                localStorage.setItem("sh_pos_night_mode", true)
                self.state.sh_pos_night_mode = true
            }
            if(self.pos && self.pos.config && self.pos.config.sh_pos_night_mode){
                 if (localStorage.getItem("sh_pos_night_mode") == 'true') {
                    localStorage.setItem("sh_pos_night_mode", true)
                }
                else{
                    localStorage.setItem("sh_pos_night_mode", true)
                }
            }
        }, 500);
    },
    change_mode(){
        if(this.pos.config.sh_pos_night_mode){
            $(".pos").toggleClass("sh_pos_night_mode")
            $(".icon-moon").toggleClass("fa-sun-o fa-moon-o")
            localStorage.setItem("sh_pos_night_mode", $(".pos").hasClass("sh_pos_night_mode"))
        }
    },
    get cart_item_count(){
        if(this && this.pos && this.pos.pos_theme_settings_data && this.pos.pos_theme_settings_data[0].display_cart_order_item_count && this.pos.get_order()){
            return this.pos.get_order().get_orderlines().length
        }else{
            return 0
        }
    }
});

/** @odoo-module */

import { ProductsWidget } from "@point_of_sale/app/screens/product_screen/product_list/product_list";
import { ProductListItem } from "@sh_pos_all_in_one_retail/static/sh_pos_theme_responsive/overrides/components/product_screen/ProductListItem";
import { patch } from "@web/core/utils/patch";
import { onMounted } from "@odoo/owl";
import { useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

ProductsWidget.components['ProductListItem'] =   ProductListItem 

patch(ProductsWidget.prototype, {
    setup() {
        super.setup()
        this.pos.isMobile = false
        onMounted(this.onMounted);
        
    },
    onMounted() {
        if(this && this.pos && this.pos.pos_theme_settings_data && this.pos.pos_theme_settings_data[0] && this.pos.pos_theme_settings_data[0].sh_pos_switch_view){
            if(this.pos.pos_theme_settings_data[0].sh_default_view == 'grid_view'){
                $('.product_grid_view').addClass('highlight')
                $('.sh_product_list_view').addClass('hide_sh_product_list_view')
            }
            if(this.pos.pos_theme_settings_data[0].sh_default_view == 'list_view'){
                $('.product_list_view').addClass('highlight')
                $('.product-list-container').addClass('hide_product_list_container')
            }
        }
        if(this.ui.isSmall){
            this.pos.isMobile = true
            $('.sh_product_list_view').addClass('hide_sh_product_list_view')
            $('.product-list-container').removeClass('hide_product_list_container')
        }
    }
});

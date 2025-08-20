/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { patch } from "@web/core/utils/patch";

patch(ProductScreen.prototype, {
    getNumpadButtons(){
        let res = super.getNumpadButtons()
        for(let val of res){
            if(this && this.pos && this.pos.user && this.pos.user.groups_id && this.pos.config.group_disable_qty && this.pos.config.group_disable_qty[0]){
                if(val.value == "quantity"){
                    if(this.pos.user.groups_id.indexOf(this.pos.config.group_disable_qty[0]) !== -1){
                       val["disabled"]  = true
                       this.pos.numpadMode = ""
                    }
                }
            }
            if(this && this.pos && this.pos.user && this.pos.user.groups_id && this.pos.config.group_disable_plus_minus && this.pos.config.group_disable_plus_minus[0]){
                if(val.value == "-"){
                    if(this.pos.user.groups_id.indexOf(this.pos.config.group_disable_plus_minus[0]) !== -1){
                        val["disabled"]  = true
                    }
                }
            }
            if(this && this.pos && this.pos.user && this.pos.user.groups_id && this.pos.config.group_disable_discount && this.pos.config.group_disable_discount[0]){
                if(val.value == "discount"){
                    if(this.pos.user.groups_id.indexOf(this.pos.config.group_disable_discount[0]) !== -1){
                        val["disabled"]  = true
                    }
                }
            }
            if(this && this.pos && this.pos.user && this.pos.user.groups_id && this.pos.config.group_disable_price && this.pos.config.group_disable_price[0]){
                if(val.value == "price"){
                    if(this.pos.user.groups_id.indexOf(this.pos.config.group_disable_price[0]) !== -1){
                        val["disabled"]  = true
                    }
                }
            }
            if(this && this.pos && this.pos.user && this.pos.user.groups_id && this.pos.config.group_disable_remove && this.pos.config.group_disable_remove[0]){
                if(val.value == "Backspace"){
                    if(this.pos.user.groups_id.indexOf(this.pos.config.group_disable_remove[0]) !== -1){
                        val["disabled"]  = true
                    }
                }
            }
            if(this && this.pos && this.pos.user && this.pos.user.groups_id && this.pos.config.group_disable_numpad && this.pos.config.group_disable_numpad[0]){
                if(val.value != "Backspace" && val.value != "price" && val.value != "discount" && val.value != "-" && val.value != "quantity"){
                    if(this.pos.user.groups_id.indexOf(this.pos.config.group_disable_numpad[0]) !== -1){
                        val["disabled"]  = true
                    }
                }
            }
        }
        return res
    }
});










// odoo.define("sh_pos_access_rights.ProductScreen", function (require) {
//     "use strict";

//     const ProductScreen = require("point_of_sale.ProductScreen");
//     const Registries = require("point_of_sale.Registries");
//     const NumberBuffer = require('point_of_sale.NumberBuffer');

//     const ShProductScreen = (ProductScreen) =>
//         class extends ProductScreen {
//             _setValue(val) {
//                 var self = this
//                 if (this.pos.numpadMode === 'quantity') {
//                     if (self.pos.user.groups_id.indexOf(self.pos.config.group_disable_qty[0]) === -1) {
//                         super._setValue(val)
//                     } else {
//                         NumberBuffer.reset();
//                     }
//                 }else{
//                     super._setValue(val)
//                 }
//             }
//         };
//         Registries.Component.extend(ProductScreen, ShProductScreen);
// });
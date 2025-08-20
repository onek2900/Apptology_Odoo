// /** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { TicketScreen } from "@point_of_sale/app/screens/ticket_screen/ticket_screen";
import { patch } from "@web/core/utils/patch";

patch(TicketScreen.prototype, {
    get allowNewOrders() {
        if(this.pos.user.groups_id.indexOf(this.pos.config.group_disable_hide_orders[0]) === -1){
        if(this && this.pos && this.pos.user && this.pos.user.groups_id && this.pos.config.group_disable_hide_orders && this.pos.config.group_disable_hide_orders[0]){
                return true;
            }else{
                return false;
            }
        }
    },
    shouldHideDeleteButton(order) {
        let res =  super.shouldHideDeleteButton(order)
        if(this && this.pos && this.pos.user && this.pos.user.groups_id && this.pos.config.group_disable_hide_orders && this.pos.config.group_disable_hide_orders[0]){
            if(this.pos.user.groups_id.indexOf(this.pos.config.group_disable_hide_orders[0]) === -1){
                return res;
            }else{
                return true;
            }
        }
    }
});

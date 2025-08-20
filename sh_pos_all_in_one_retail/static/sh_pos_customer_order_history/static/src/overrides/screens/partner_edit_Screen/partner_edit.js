/** @odoo-module */

import { _t } from "@web/core/l10n/translation";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { PartnerDetailsEdit } from "@point_of_sale/app/screens/partner_list/partner_editor/partner_editor";
import { patch } from "@web/core/utils/patch";

patch(PartnerDetailsEdit.prototype, {
    setup() {
        super.setup(...arguments);
        this.selected_order = null
    },
    shSelectOrder(order){
        if ($('.sh_hide_order_lines'+order.id).hasClass('sh_highlight')){
            $('.sh_hide_order_lines'+order.id).removeClass('sh_highlight')
        } else{
            $('.sh_hide_order_lines').removeClass('sh_highlight')
            $('.sh_hide_order_lines'+order.id).addClass('sh_highlight')
        } 
        if ($('.sh_client_order_line'+order.id).hasClass('highlight')){
            $('.sh_client_order_line'+order.id).removeClass('highlight')
        } else{
            $('.sh_client_order_line').removeClass('highlight')
            $('.sh_client_order_line'+order.id).addClass('highlight')
        } 
    }
});

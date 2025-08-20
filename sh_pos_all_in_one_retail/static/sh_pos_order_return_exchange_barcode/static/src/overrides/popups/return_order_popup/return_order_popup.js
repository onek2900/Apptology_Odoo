/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { ReturnOrderPopup } from "@sh_pos_all_in_one_retail/static/sh_pos_order_return_exchange/apps/popups/return_order_popup/return_order_popup";
import { onMounted } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";


patch(ReturnOrderPopup.prototype, {
    setup(){
        super.setup()
        onMounted(this.onMounted);
        this.pos = usePos();
        this.operation_type = "return";
    },
    onMounted() {
        var self = this;
        $(".complete_exchange").hide()
        $(".exchange").hide()
        $(".sh_same_product_checkbox").hide()
       
        $("#exchange_radio").click(function () {
            $(".complete_exchange").show()
            $(".exchange").show()
            $(".complete_return").hide()
            $(".return").hide()
            $(".sh_same_product_checkbox").show()
        });
        $("#return_radio").click(function () {
            $(".sh_same_product_checkbox").hide()
            $(".complete_exchange").hide()
            $(".exchange").hide()
            $(".complete_return").show()
            $(".return").show()
        });
       
    }
})
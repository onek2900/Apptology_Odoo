/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
import { onMounted, useRef, useState } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";


export class DiscountPopupWidget extends AbstractAwaitablePopup {
    static template = "sh_pos_discount.DiscountPopupWidget";
   
    setup() {
        super.setup();
        this.pos = usePos();
    }
    async confirm() {
        var self = this;
        var apply_discount_code_value = [];
        var apply_discount_code = [];
        var apply_discount_value = 0;
        var highlightRows = document.querySelectorAll("tr.highlight");
        for (var i = 0; i < highlightRows.length; i++) {
            var each_highlight_row = highlightRows[i];
            apply_discount_code_value.push(each_highlight_row.dataset.code + " ( " + each_highlight_row.dataset.value + "% )");
            apply_discount_code.push(each_highlight_row.dataset.code);
            apply_discount_value += parseInt(each_highlight_row.dataset.value);
        };
        self.pos.get_order().get_selected_orderline().set_line_discount(apply_discount_code_value);
        self.pos.get_order().get_selected_orderline().set_line_discount_code(apply_discount_code);
        self.pos.get_order().get_selected_orderline().set_discount(apply_discount_value);
        super.confirm()
    }
    async onClickDiscountRow(event) {
        var value = $(event.currentTarget).data("value");
        if ($(event.currentTarget)[0].classList.length == 2) {
            $(event.currentTarget)[0].classList.remove("highlight");
        } else {
            $(event.currentTarget)[0].classList.add("highlight");
        }
    }
}

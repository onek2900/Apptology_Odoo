/** @odoo-module */

import { CashOpeningPopup } from "@point_of_sale/app/store/cash_opening_popup/cash_opening_popup";
import { patch } from "@web/core/utils/patch";

patch(CashOpeningPopup.prototype, {
    async confirm() {
        super .confirm()
        this.pos.cash_register_balance_start = 
            this.pos.pos_session.cash_register_balance_start|| 0
    }
})
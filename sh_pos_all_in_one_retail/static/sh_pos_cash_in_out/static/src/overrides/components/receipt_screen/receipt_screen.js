/** @odoo-module */

import { ReceiptScreen } from "@point_of_sale/app/screens/receipt_screen/receipt_screen";
import { patch } from "@web/core/utils/patch";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { CashInOutStatementReceipt } from "@sh_pos_all_in_one_retail/static/sh_pos_cash_in_out/app/screens/CashInOutStatementReceipt/CashInOutStatementReceipt"
patch(ReceiptScreen.prototype, {
    setup() {
        super.setup(...arguments);
        this.pos = usePos();
    },
    receiptDone() {
        this.pos.cash_in_out_receipt = false;
        this.pos.cash_in_out_statement_receipt = false;
        this.pos.get_order()._printed = false;
        this.pos.showScreen("ProductScreen");
    },
});
ReceiptScreen.components['CashInOutStatementReceipt'] = CashInOutStatementReceipt
/** @odoo-module */
    
    
import {  Component } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { registry } from "@web/core/registry";
import { ReceiptScreen } from "@point_of_sale/app/screens/receipt_screen/receipt_screen";

export class CashInOutStatementReceipt extends Component {
    
    static template = "sh_pos_cash_in_out.CashInOutStatementReceipt";
    

        setup() {
            super.setup();
            this.pos = usePos();
        } 
    }

registry.category("pos_screens").add("CashInOutStatementReceipt", CashInOutStatementReceipt);

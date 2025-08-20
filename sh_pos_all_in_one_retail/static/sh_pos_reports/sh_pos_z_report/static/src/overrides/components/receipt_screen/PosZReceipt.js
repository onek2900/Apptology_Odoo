/** @odoo-module */
    
    
import {  Component } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { registry } from "@web/core/registry";
import { ReceiptHeader } from "@point_of_sale/app/screens/receipt_screen/receipt/receipt_header/receipt_header";

export class PosZReceipt extends Component {
    
    static template = "sh_pos_z_report.PosZReceipt";
    static components = {
        ReceiptHeader,
    };
    setup() {
        super.setup();
        this.pos = usePos();
    } 
}

registry.category("pos_screens").add("PosZReceipt", PosZReceipt);

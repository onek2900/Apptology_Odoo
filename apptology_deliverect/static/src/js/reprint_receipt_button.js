/** @odoo-module */

import { ReprintReceiptButton } from "@point_of_sale/app/screens/ticket_screen/reprint_receipt_button/reprint_receipt_button";
import { patch } from "@web/core/utils/patch";

patch(ReprintReceiptButton.prototype, {
    setup() {
        super.setup(...arguments);
        this.reloadData();
    },
    async reloadData(){
        await this.pos.load_server_data();
    }
});
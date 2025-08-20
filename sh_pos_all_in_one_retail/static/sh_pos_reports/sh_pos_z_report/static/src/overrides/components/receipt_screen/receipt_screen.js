/** @odoo-module */

import { ReceiptScreen } from "@point_of_sale/app/screens/receipt_screen/receipt_screen";
import { patch } from "@web/core/utils/patch";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { PosZReceipt } from "@sh_pos_all_in_one_retail/static/sh_pos_reports/sh_pos_z_report/overrides/components/receipt_screen/PosZReceipt"
import { useState, onMounted } from "@odoo/owl";

patch(ReceiptScreen.prototype, {
    setup() {
        super.setup(...arguments);
        this.pos = usePos();
        onMounted(() => {
            if(this.pos.is_z_report_receipt && $('.next')){
                $('.next').text('Close')
            }
        })
    },
    orderDone() {
        this.pos.is_z_report_receipt = false;
        super.orderDone()
    },
    async printReceipt() {
        if(this.pos.is_z_report_receipt){
            this.buttonPrintReceipt.el.className = "fa fa-fw fa-spin fa-circle-o-notch";
            const isPrinted = await this.printer.print(
                PosZReceipt,
                {
                    data: this.pos.get_order().export_for_printing(),
                    formatCurrency: this.env.utils.formatCurrency,
                },
                { webPrintFallback: true }
            );

            if (isPrinted) {
                this.currentOrder._printed = true;
            }

            if (this.buttonPrintReceipt.el) {
                this.buttonPrintReceipt.el.className = "fa fa-print";
            }
        }else{
            super.printReceipt()
        }
    }
});
ReceiptScreen.components['PosZReceipt'] = PosZReceipt
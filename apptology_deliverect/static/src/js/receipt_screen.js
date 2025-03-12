/** @odoo-module */

import { Navbar } from "@point_of_sale/app/navbar/navbar";
import { patch } from "@web/core/utils/patch";
import { useService,useBus } from "@web/core/utils/hooks";
import { useState,onWillUnmount,useRef } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { ReceiptScreen } from "@point_of_sale/app/screens/receipt_screen/receipt_screen";
import { onlineOrderReceipt } from "./online_order_receipt"

patch(ReceiptScreen.prototype, {
    setup(){
        super.setup();
        this.buttonOnlineOrderPrintReceipt = useRef("online-order-print-receipt-button");
    },
    async printOnlineReceipt() {

        console.log("AMR :",this.pos.selectedOrder.server_id)
        const currentOrder = this.pos.pos_orders.filter(order => order.id === this.pos.selectedOrder.server_id);
        console.log("AMR 2 :",currentOrder)
        this.buttonOnlineOrderPrintReceipt.el.className = "fa fa-fw fa-spin fa-circle-o-notch";
        const isPrinted = await this.printer.print(
            onlineOrderReceipt,
            {
                data: {
                    ...this.pos.get_order().export_for_printing(),
                    isBill: this.isBill,
                    orderData: currentOrder[0],
                },
                formatCurrency: this.env.utils.formatCurrency,
            },
            { webPrintFallback: true }
        );
        if (isPrinted) {
            this.currentOrder._printed = true;
        }

        if (this.buttonOnlineOrderPrintReceipt.el) {
            this.buttonOnlineOrderPrintReceipt.el.className = "fa fa-print";
        }
    }
});
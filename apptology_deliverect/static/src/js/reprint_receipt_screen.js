/** @odoo-module */
import { patch } from "@web/core/utils/patch";
import { useService,useBus } from "@web/core/utils/hooks";
import { useState,onWillUnmount,useRef } from "@odoo/owl";
import { ReprintReceiptScreen } from "@point_of_sale/app/screens/receipt_screen/reprint_receipt_screen";
import { onlineOrderReceipt } from "./online_order_receipt"
import { OrderReceipt } from "@point_of_sale/app/screens/receipt_screen/receipt/order_receipt";

ReprintReceiptScreen.components ={
...ReprintReceiptScreen.components,
onlineOrderReceipt
}
patch(ReprintReceiptScreen.prototype, {
    tryOnlineOrderReprint() {
        const currentOrder = this.pos.pos_orders.filter(order => order.id === this.props.order.server_id);
        const orderLines = this.props.order.orderlines.map(order => {
            return {
                lineId: order.id,
                name: order.full_product_name,
                qty: order.quantity,
                note: order.note,
            };
        });
        this.printer.print(
            onlineOrderReceipt,
            {
                data: {
                    ...this.props.order.export_for_printing(),
                    orderData: currentOrder[0],
                    orderLineData: orderLines
                },
                formatCurrency: this.env.utils.formatCurrency,
            },
            { webPrintFallback: true }
        );
    }
});
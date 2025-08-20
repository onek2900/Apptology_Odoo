/** @odoo-module */

import { ReceiptScreen } from "@point_of_sale/app/screens/receipt_screen/receipt_screen";
import { OrderReceipt } from "@point_of_sale/app/screens/receipt_screen/receipt/order_receipt";
import { registry } from "@web/core/registry";

export class ShReceiptScreen extends ReceiptScreen {
    static template = "ShReceiptScreen";
    static components = { OrderReceipt };
    setup(){
        super.setup(...arguments);
        this.receipt_type = "standard";
        this.is_not_standard_size = false;
        var config = this.pos.config;
        if (
        config.sh_enable_a3_receipt ||
        config.sh_enable_a4_receipt ||
        config.sh_enable_a5_receipt
        ) {
        if (config.sh_default_receipt) {
            this.receipt_type = config.sh_default_receipt;
        }
        }
    }
    confirm() {
        this.pos.showScreen('ProductScreen')
    }
    /**
     * @override
     */
    async printReceipt() {
        var self = this;
        this.buttonPrintReceipt.el.className = "fa fa-fw fa-spin fa-circle-o-notch";
        const isPrinted = await this.printer.print(
            OrderReceipt,
            {
                data: self.props.order.export_for_printing(),
                formatCurrency: this.env.utils.formatCurrency,
            },
            { webPrintFallback: true }
        );

        if (isPrinted) {
            this.props.order._printed = true;
        }

        if (this.buttonPrintReceipt.el) {
            this.buttonPrintReceipt.el.className = "fa fa-print";
        }
        this.currentOrder._printed = false;
    }
    
    get order_data(){
        var order = this.props.order.export_for_printing()
        var date = new Date(this.props.selected_order.date_order+' PM UTC');
        order['date']  =  date.toLocaleString()
        return order
    }
    get isBill() {
        return true;
    }
}

registry.category("pos_screens").add("ShReceiptScreen", ShReceiptScreen);

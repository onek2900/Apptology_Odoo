/** @odoo-module **/

import { Component } from "@odoo/owl";
import { ReceiptHeader } from "@point_of_sale/app/screens/receipt_screen/receipt/receipt_header/receipt_header";

export class PrinterReceipt extends Component {
    static template = "apptology_pos_kitchen_printing.PrinterReceipt";
    static components = {
        ReceiptHeader,
    };

    static props = {
        data: Object,
        headerData: Object,
        printer: Object,
    };
}

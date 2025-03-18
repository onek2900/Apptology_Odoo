/** @odoo-module */

import { usePos } from "@point_of_sale/app/store/pos_hook";
import { registry } from "@web/core/registry";
import { Component,useState,onWillUnmount } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { ConfirmPopup } from "@point_of_sale/app/utils/confirm_popup/confirm_popup";
import { Orderline } from "@point_of_sale/app/generic_components/orderline/orderline";
import { OrderWidget } from "@point_of_sale/app/generic_components/order_widget/order_widget";
import { ReceiptHeader } from "@point_of_sale/app/screens/receipt_screen/receipt/receipt_header/receipt_header";
import { _t } from "@web/core/l10n/translation";

export class onlineOrderReceipt extends Component {
    static template = "apptology_deliverect.OnlineOrderReceipt";
    static components = {
        Orderline,
        OrderWidget,
        ReceiptHeader,
    };
    static props = {
        data: Object,
        formatCurrency: Function,
    };
    omit(...args) {
        return omit(...args);
    }
}
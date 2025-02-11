/** @odoo-module */

import { usePos } from "@point_of_sale/app/store/pos_hook";
import { OrderReceipt } from "@point_of_sale/app/screens/receipt_screen/receipt/order_receipt";
import { registry } from "@web/core/registry";
import { Component,useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class OnlineOrderScreen extends Component {
    static template = "point_of_sale.OnlineOrderScreen";
    setup() {
        this.state = useState({
            lines: this.env.services.pos.open_orders_json.map(order => ({
                ...order,
                date_order: this.formatDate(order.date_order),
            })),
        });

        console.log('state :', this.state);
    }
    formatDate(dateStr) {
        if (!dateStr) return dateStr;
        let datePart = dateStr.split('+')[0];
        let dateObj = new Date(datePart);

        let month = String(dateObj.getMonth() + 1).padStart(2, '0');
        let day = String(dateObj.getDate()).padStart(2, '0');
        let year = dateObj.getFullYear();
        let hours = String(dateObj.getHours()).padStart(2, '0');
        let minutes = String(dateObj.getMinutes()).padStart(2, '0');
        let seconds = String(dateObj.getSeconds()).padStart(2, '0');

        return `${month}/${day}/${year} ${hours}:${minutes}:${seconds}`;
    }
    onApproveOrder(orderId) {
        console.log('approved')
//        change order state
    }

    onDeclineOrder(orderId) {
        console.log('declined')
//        change order state
    }

}

registry.category("pos_screens").add("OnlineOrderScreen", OnlineOrderScreen);

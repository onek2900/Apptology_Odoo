/** @odoo-module */

import { usePos } from "@point_of_sale/app/store/pos_hook";
import { OrderReceipt } from "@point_of_sale/app/screens/receipt_screen/receipt/order_receipt";
import { registry } from "@web/core/registry";
import { Component,useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class OnlineOrderScreen extends Component {
    static template = "point_of_sale.OnlineOrderScreen";
    setup() {
        this.orm = useService("orm");
        this.state = useState({
            lines: [],
            orderDetails:{},
            orderLines:[],
            respondedOrders:[]
        });
        this.refreshLines();
    }
    async refreshLines(remove_id=null) {
        console.log('refresh lines :',remove_id,typeof remove_id)
        const openOrders = this.env.services.pos.open_orders_json;
        const refreshedLines = openOrders
            .filter(item => !item.ticket_code && item.state === 'draft' && !this.state.respondedOrders.includes(item.id)
            )
            .map(order => ({
                id:order.id,
                lines: order.lines.map(line => {
                    const { full_product_name,price_subtotal,price_subtotal_incl,price_unit,qty,id } = line[2];
                        return {
                                id,
                                full_product_name,
                                price_subtotal: price_subtotal / 100,
                                price_subtotal_incl:price_subtotal/100,
                                price_unit:price_unit/100,
                                qty,
                            };
                }),
                amount_total:order.amount_total,
                amount_tax:order.amount_tax,
                name:order.name,
                partner_id:order.partner_id,
                ticket_code:order.ticked_code,
                date_order: this.formatDate(order.date_order),
                state:order.state
            }));
        console.log('refreshed lines :',refreshedLines)
        this.state.orderDetails=[];
        this.state.orderLines=[];
        this.state.lines = refreshedLines;
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
    async onApproveOrder(orderId) {
        await this.orm.call(
            "pos.order",
            "update_order_status",
            [orderId],
            { status: 'approved' },
        );
        this.state.respondedOrders.push(orderId)
        this.refreshLines(orderId);
    }

    async onDeclineOrder(orderId) {
       await this.orm.call(
            "pos.order",
            "update_order_status",
            [orderId],
            { status: 'cancelled'},
        )
        this.state.respondedOrders.push(orderId)
        this.refreshLines(orderId);
    }
    onClickOrder(line){
        console.log('click line :',line)
        var orderDetails={
            'amountTotal':line.amount_total,
            'amountTax':line.amount_tax,
        }
        this.state.orderDetails=orderDetails
        this.state.orderLines=line.lines

    }

}

registry.category("pos_screens").add("OnlineOrderScreen", OnlineOrderScreen);

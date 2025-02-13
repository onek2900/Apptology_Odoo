/** @odoo-module */

import { usePos } from "@point_of_sale/app/store/pos_hook";
import { OrderReceipt } from "@point_of_sale/app/screens/receipt_screen/receipt/order_receipt";
import { registry } from "@web/core/registry";
import { Component,useState,onWillUnmount } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class OnlineOrderScreen extends Component {
    static template = "point_of_sale.OnlineOrderScreen";
    setup() {
        this.orm = useService("orm");
        this.state = useState({
            clickedOrder:{},
            openOrders:[],
        });
        this.initiateServices();
        onWillUnmount(()=>clearInterval(this.pollingInterval))
    }
    async initiateServices(){
        this.fetchOpenOrders();
        this.startPollingOrders();
    }
    async fetchOpenOrders(){
        try {
            const openOrders = await this.orm.call("pos.order", "get_open_orders", []);
            this.state.openOrders=openOrders
        } catch (error) {
            console.error("Error fetching open orders:", error);
        }
    }
    async startPollingOrders() {
        this.pollingInterval = setInterval(async () => {
            try {
                console.log("Fetching fresh orders...");
                const openOrders = await this.orm.call("pos.order", "get_open_orders", []);
                this.state.openOrders = openOrders;
                console.log("Fetched fresh orders:", openOrders);
            } catch (error) {
                console.error("Error fetching open orders:", error);
            }
        }, 10000);
    }
    async onApproveOrder(orderId) {
        console.log('approve order')
        await this.orm.call(
            "pos.order",
            "update_order_status",
            [orderId],
            { status: 'approved' },
        );
        this.fetchOpenOrders();
    }

    async onDeclineOrder(orderId) {
        console.log('decline order')
       await this.orm.call(
            "pos.order",
            "update_order_status",
            [orderId],
            { status: 'declined'},
        )
        this.fetchOpenOrders();
    }
    onClickOrder(order){
        this.state.clickedOrder=order
    }

}

registry.category("pos_screens").add("OnlineOrderScreen", OnlineOrderScreen);

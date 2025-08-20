/** @odoo-module */

import { usePos } from "@point_of_sale/app/store/pos_hook";
import { registry } from "@web/core/registry";
import { Component,useState,onWillUnmount } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { ConfirmPopup } from "@point_of_sale/app/utils/confirm_popup/confirm_popup";
import { _t } from "@web/core/l10n/translation";
import { onlineOrderReceipt } from "./online_order_receipt";

export class OnlineOrderScreen extends Component {
    static template = "point_of_sale.OnlineOrderScreen";
    setup() {
        this.pos = usePos();
        this.orm = useService("orm");
        this.rpc = useService("rpc");
        this.popup = useService("popup");
        this.printer = useService("printer");
        this.state = useState({
            clickedOrder:{},
            openOrders:[],
            currency_symbol:this.env.services.pos.currency.symbol,
            isAutoApprove:this.pos.config.auto_approve
        });
        this.channel=`new_pos_order_${this.pos.config.id}`;
        this.busService = this.env.services.bus_service;
        this.busService.addChannel(this.channel);
        this.busService.addEventListener('notification', ({detail: notifications})=>{
            notifications = notifications.filter(item => item.payload.channel === this.channel)
            notifications.forEach(item => {
                    this.fetchOpenOrders();
                })
        });
        this.initiateServices();
        onWillUnmount(()=>clearInterval(this.pollingInterval))
    }
    /**
     * Initiates services by fetching open orders and starting polling.
     */
    async initiateServices(){
        this.fetchOpenOrders();
        this.startPollingOrders();
    }
    /**
     * To get time only from datetime
     */
    formatTime(dateStr) {
    const date = new Date(dateStr);
    const time = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit',second: '2-digit'  });
    const formattedDate = date.toLocaleDateString('en-CA'); // YYYY-MM-DD
    return {
        time: time,
        date: formattedDate,
    };
}
    /**
     * Auto receipt printing
     */
   async printReceipt(order) {
        try {
        const [exportedOrder] = await this.orm.call("pos.order", "export_order_for_ui", [order]);
        if (!exportedOrder) {
            console.error("No order data returned from backend.");
            return;
        }
        const currentOrder = this.pos.pos_orders.find(o => o.id === order);
        const orderLines = [];
        exportedOrder.lines.forEach(lineArr => {
        const line = lineArr[2];
    if (line && line.id) {
        orderLines.push({
            lineId: line.id,
            name: line.full_product_name,
            qty: line.qty,
            note: line.note,
        });
    }
});
        this.printer.print(
            onlineOrderReceipt,
            {
                data: {
                    ...exportedOrder,
                    orderData: currentOrder || exportedOrder,
                    orderLineData: orderLines,
                    headerData: {company:this.pos.company}
                },
                formatCurrency: this.env.utils.formatCurrency,
            },
            { webPrintFallback: true }
        );
    } catch (error) {
        console.error("Failed to print online order receipt:", error);
    }
}
    /**
     * Fetches open online orders.
     */
    async fetchOpenOrders(){
        try {
            const openOrders = await this.orm.call("pos.order", "get_open_orders", [],{config_id:this.pos.config.id});
            const unpaidOrders = await this.pos.get_order_list().filter(order => order.name.includes("Online-Order"));
            this.state.openOrders = openOrders;
        } catch (error) {
            console.error("Error fetching open orders:", error);
        }
    }
    /**
     * Starts polling for open orders every 10 seconds.
     */
    async startPollingOrders() {
        this.pollingInterval = setInterval(async () => this.fetchOpenOrders(), 10000);
    }
    /**
     * Approves an online order.
     *
     * @param {number} orderId - The ID of the order to approve.
     */
    async onApproveOrder(orderId) {
       this.printReceipt(orderId)
        await this.orm.call(
            "pos.order",
            "update_order_status",
            [orderId],
            { status: 'approved'},
        );
        this.env.bus.trigger('online_order_state_update');
        this.fetchOpenOrders();
    }
    /**
     * Declines an online order after confirmation.
     *
     * @param {number} orderId - The ID of the order to decline.
     */
    async onDeclineOrder(orderId) {
        const {confirmed} =  await this.popup.add(ConfirmPopup, {
            title: _t("Confirmation"),
            body: _t(
                "Are you sure you want to cancel the order ?"
            ),
        });
        if (confirmed){
                await this.orm.call(
                        "pos.order",
                        "update_order_status",
                        [orderId],
                        { status: 'declined'},
                        )
                this.env.bus.trigger('online_order_state_update');
                this.fetchOpenOrders();
            }
    }
    /**
    * Ready function to make the order stage ready
    */
    async done_order(order){
    await this.rpc("/pos/kitchen/order_status", {
                method: 'order_progress_change',
                order_id: Number(order.id),
            });
            if (order) {
                order.order_status = 'ready';
                }
    }
    /**
     * Closes the online order screen and navigates to the product screen.
     */
    closeOnlineOrderScreen(){
        this.env.services.pos.showScreen("ProductScreen");
    }
    /**
     * Updates the clicked order state to show its details.
     *
     * @param {Object} order - The order object that was clicked.
     */
    onClickOrder(order){
        this.state.clickedOrder = order
    }
    /**
     * Finalizes an online order.
     *
     * @param {Object} order - The order object to finalize.
     */
    async finalizeOrder(order){
        await this.orm.call("pos.order", "update_order_status", [order.id],{status:'finalized'});
        this.state.clickedOrder = {};
        this.fetchOpenOrders();
    }
    /**
     * Redirects to the ticket screen when an order is double-clicked.
     *
     * @param {Object} order - The order object that was double-clicked.
     */
    async onDoubleClick(order){
        if (order.online_order_status && ['approved', 'finalized'].includes(order.online_order_status)){
            const searchDetails = {
                fieldName: "RECEIPT_NUMBER",
                searchTerm: order.pos_reference,
            };
            const ticketFilter = order.state=='paid'?"SYNCED":"ACTIVE_ORDERS"
            await this.pos._syncTableOrdersFromServer();
            this.pos.showScreen("TicketScreen", {
                ui: { filter: ticketFilter, searchDetails },
            });
        }
    }
}
registry.category("pos_screens").add("OnlineOrderScreen", OnlineOrderScreen);

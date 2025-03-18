/** @odoo-module */

import { usePos } from "@point_of_sale/app/store/pos_hook";
import { registry } from "@web/core/registry";
import { Component,useState,onWillUnmount } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { ConfirmPopup } from "@point_of_sale/app/utils/confirm_popup/confirm_popup";
import { _t } from "@web/core/l10n/translation";

export class OnlineOrderScreen extends Component {
    static template = "point_of_sale.OnlineOrderScreen";
    setup() {
        this.pos = usePos();
        this.orm = useService("orm");
        this.popup = useService("popup");
        this.state = useState({
            clickedOrder:{},
            openOrders:[],
            currency_symbol:this.env.services.pos.currency.symbol
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
    async initiateServices(){
//    function to initiate services
        this.fetchOpenOrders();
        this.startPollingOrders();
    }
    async fetchOpenOrders(){
//    function to fetch open online orders
        try {
            const openOrders = await this.orm.call("pos.order", "get_open_orders", [],{config_id:this.pos.config.id});
            const unpaidOrders = await this.pos.get_order_list().filter(order => order.name.includes("Online-Order"));
            this.state.openOrders = openOrders;
        } catch (error) {
            console.error("Error fetching open orders:", error);
        }
    }
    async startPollingOrders() {
//    function to start polling for open orders every 10 seconds
        this.pollingInterval = setInterval(async () => this.fetchOpenOrders(), 10000);
    }
    async onApproveOrder(orderId) {
//    function to approve an online order
        await this.orm.call(
            "pos.order",
            "update_order_status",
            [orderId],
            { status: 'approved'},
        );
        this.env.bus.trigger('online_order_state_update');
        this.fetchOpenOrders();
    }

    async onDeclineOrder(orderId) {
//    function to decline an online order
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
    closeOnlineOrderScreen(){
//    function to close the online order screen
        this.env.services.pos.showScreen("ProductScreen");
    }
    onClickOrder(order){
//    function to show clicked order details
        this.state.clickedOrder = order

    }
    async finalizeOrder(order){
//    function to finalize an online order
        await this.orm.call("pos.order", "update_order_status", [order.id],{status:'finalized'});
        this.state.clickedOrder = {};
        this.fetchOpenOrders();
    }
}
registry.category("pos_screens").add("OnlineOrderScreen", OnlineOrderScreen);

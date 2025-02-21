/** @odoo-module */

import { usePos } from "@point_of_sale/app/store/pos_hook";
import { OrderReceipt } from "@point_of_sale/app/screens/receipt_screen/receipt/order_receipt";
import { registry } from "@web/core/registry";
import { Component,useState,onWillUnmount } from "@odoo/owl";
import { useService,useBus } from "@web/core/utils/hooks";
import { ConfirmPopup } from "@point_of_sale/app/utils/confirm_popup/confirm_popup";
import { _t } from "@web/core/l10n/translation";

export class OnlineOrderScreen extends Component {
    static template = "point_of_sale.OnlineOrderScreen";
    setup() {
        this.orm = useService("orm");
        this.popup = useService("popup");
        this.state = useState({
            clickedOrder:{},
            openOrders:[],
            currency_symbol:this.env.services.pos.currency.symbol
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
                const openOrders = await this.orm.call("pos.order", "get_open_orders", []);
                this.state.openOrders = openOrders;
            } catch (error) {
                console.error("Error fetching open orders:", error);
            }
        }, 10000);
    }
    async onApproveOrder(orderId) {
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
        this.env.services.pos.showScreen("ProductScreen");
    }
    onClickOrder(order){
        this.state.clickedOrder = order
    }

}

registry.category("pos_screens").add("OnlineOrderScreen", OnlineOrderScreen);

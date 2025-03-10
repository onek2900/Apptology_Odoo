/** @odoo-module */

import { Navbar } from "@point_of_sale/app/navbar/navbar";
import { patch } from "@web/core/utils/patch";
import { useService,useBus } from "@web/core/utils/hooks";
import { useState,onWillUnmount } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";

patch(Navbar.prototype, {
    setup() {
        super.setup();
        this.busService = this.env.services.bus_service;
        this.channel=`new_pos_order_${this.pos.config.id}`;
        this.busService.addChannel(this.channel);
        this.busService.addEventListener('notification', ({detail: notifications})=>{
            notifications = notifications.filter(item => item.payload.channel === this.channel)
            notifications.forEach(item => {
                this.notification.add(_t("New Order Received"), { type: "info",
                                                         sticky: true});
                this.onlineOrderCount();
                })
        });
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");
        this.state=useState({
            onlineOrderCount:0
        })
        this.initiateServices();
        useBus(this.env.bus, 'online_order_state_update', (ev) =>{
            this.onlineOrderCount();
        });
        onWillUnmount(()=>clearInterval(this.pollingOrderCountInterval));
        },
    initiateServices(){
//    function to initiate services
        this.onlineOrderCount();
        this.startPollingOrderCount();
    },
    async autoApproveOrders(){
//    function to auto approve online orders
        await this.orm.call("pos.config", "toggle_approve", [this.pos.config.id]);
        window.location.reload();
    },
    async onClickOnlineOrder() {
//    function to show online order screen
        await this.pos.showScreen("OnlineOrderScreen");
    },
    async onlineOrderCount() {
//    function to fetch online order count
        try {
            this.state.onlineOrderCount = await this.pos.get_online_orders();
        } catch (error) {
            console.error("Error fetching online order count:", error);
        }
    },
    async startPollingOrderCount() {
//    function to start polling online order count every 10 seconds
        this.pollingOrderCountInterval=setInterval(() => {
            this.onlineOrderCount();
        }, 10000);
    },
});

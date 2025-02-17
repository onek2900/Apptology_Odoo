/** @odoo-module */

import { Navbar } from "@point_of_sale/app/navbar/navbar";
import { patch } from "@web/core/utils/patch";
import { useService,useBus } from "@web/core/utils/hooks";
import { useState,onWillUnmount,EventBus } from "@odoo/owl";

patch(Navbar.prototype, {
    setup() {
        super.setup();
        this.state=useState({
            onlineOrderCount:0
        })
        this.initiateServices();
        useBus(this.env.bus, 'online_order_state_update', (ev) =>this.onlineOrderCount());
        onWillUnmount(()=>clearInterval(this.pollingOrderCountInterval));
        },
    initiateServices(){
        this.onlineOrderCount();
        this.startPollingOrderCount();
    },
    async onClickOnlineOrder() {
        await this.pos.showScreen("OnlineOrderScreen");
    },
    async onlineOrderCount() {
        try {
            this.state.onlineOrderCount = await this.pos.get_online_orders();
        } catch (error) {
            console.error("Error fetching online order count:", error);
        }
    },
    async startPollingOrderCount() {
        this.pollingOrderCountInterval=setInterval(() => {
            this.onlineOrderCount();
        }, 10000);
    },
});

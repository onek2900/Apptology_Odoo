/** @odoo-module */

import { Navbar } from "@point_of_sale/app/navbar/navbar";
import { patch } from "@web/core/utils/patch";
import { useService,useBus } from "@web/core/utils/hooks";
import { useState,onWillUnmount,EventBus } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";

patch(Navbar.prototype, {
    setup() {
        super.setup();
        this.busService = this.env.services.bus_service;
        console.log('pos_config:',this.pos.config.id)
        this.channel=`new_pos_order_${this.pos.config.id}`;
        this.busService.addChannel(this.channel);
        this.busService.addEventListener('notification', ({detail: notifications})=>{
        console.log('notification received')
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
        this.onlineOrderCount();
        this.startPollingOrderCount();
    },
    async autoApproveOrders(){
        console.log('pos config :',this.pos.config.id)
        await this.orm.call("pos.config", "toggle_approve", [this.pos.config.id]);
        window.location.reload();
    },
    async openKitchenScreen(){
        this.action.doAction({
            type: "ir.actions.act_url",
            target: 'new',
            url: `/apptology_kitchen_screen?shop_id=${this.pos.config.id}`,
        });
    },
    async openOrderScreen(){
        const kitchenScreen = await this.orm.searchRead(
                "kitchen.screen",
                [
                    ["pos_config_id", "=", this.pos.config.id],
                ],
                ["id"]
            );
        const kitchenScreenId = kitchenScreen[0]?.id
        this.action.doAction({
            type: "ir.actions.act_url",
            target: 'new',
            url: `/apptology_order_screen?screen_id=${kitchenScreenId}`,
        });
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

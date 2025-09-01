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
        this.busService.addEventListener('notification', ({ detail: notifications }) => {
            const events = notifications.filter((n) => n.payload?.channel === this.channel);
            for (const evt of events) {
                const status = evt.payload?.order_status;
                if (!status) {
                    // Ignore noise events that do not carry an order status
                    continue;
                }
                this.playNotificationSound();
                if (status === 'success') {
                    this.notification.add(_t("New Online Order Received"), { type: "info" });
                } else if (status === 'failed') {
                    this.notification.add(_t("Failed to receive online order"), { type: "danger", sticky: true });
                } else {
                    // Unknown status; do not notify to avoid confusion
                }
                this.onlineOrderCount();
            }
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
        /**
     *  notification sound
     */
    playNotificationSound() {
    const audio = new Audio('/apptology_deliverect/static/src/sounds/notification.mp3');
    audio.play().catch((e) => {
        console.warn("Unable to play sound:", e);
    });
},
    /**
     * Fetches the online order count and starts polling.
     */
    initiateServices(){
        this.onlineOrderCount();
        this.startPollingOrderCount();
    },
    /**
     * Automatically approves online orders.
     */
    async autoApproveOrders(){
        await this.orm.call("pos.config", "toggle_approve", [this.pos.config.id]);
        window.location.reload();
    },
    /**
     * Displays the online order screen.
     */
    async onClickOnlineOrder() {
        await this.pos.showScreen("OnlineOrderScreen");
    },
    /**
     * Fetches the count of online orders.
     */
    async onlineOrderCount() {
        try {
            this.state.onlineOrderCount = await this.pos.get_online_orders();
        } catch (error) {
            console.error("Error fetching online order count:", error);
        }
    },
    /**
     * Starts polling for online order count every 30 seconds.
     */
    async startPollingOrderCount() {
        this.pollingOrderCountInterval=setInterval(() => {
            this.onlineOrderCount();
        }, 30000);
    },
});

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
        this.deliverectChannel = `new_pos_order_${this.pos.config.id}`;
        this.busService.addChannel(this.deliverectChannel);
        this.busService.addEventListener('notification', ({ detail: notifications }) => {
            try {
                const events = (notifications || []).filter((n) => {
                    const p = n && n.payload;
                    const ch = (p && (p.channel || (Array.isArray(p) && p[0]?.channel))) || null;
                    return ch === this.deliverectChannel;
                });
                for (const evt of events) {
                    const p = evt.payload;
                    const status = p?.order_status;
                    if (!status) continue;
                    this.playNotificationSound();
                    if (status === 'success') {
                        this.notification.add(_t("New Online Order Received"), { type: "info" });
                    } else if (status === 'failed' || status === 'failure') {
                        this.notification.add(_t("Failed to receive online order"), { type: "danger", sticky: true });
                    }
                    this.onlineOrderCount();
                }
            } catch (e) {
                // Non-fatal: keep POS usable even if parsing fails
                console.warn('Online order bus parse failed', e);
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
        // Refresh the counter every 10 seconds as a fallback
        this.pollingOrderCountInterval=setInterval(() => {
            this.onlineOrderCount();
        }, 10000);
    },
});

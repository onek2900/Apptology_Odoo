/** @odoo-module **/

import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";
import { onMounted, onWillUnmount } from "@odoo/owl";

patch(PaymentScreen.prototype, {
    setup() {
        super.setup(...arguments);
        this.busService = this.env.services.bus_service;
        this.channel = `pos_moneris_${this.pos.config.id}`;
        this.busService.addChannel(this.channel);

        this._onNotif = ({ detail: notifications }) => {
            const events = notifications.filter(n => (n.payload?.channel === this.channel) || n.payload === 'MONERIS_LATEST_RESPONSE');
            for (const evt of events) {
                const payload = evt.payload;
                const msg = payload?.message || payload; // either our dict or legacy type
                this._handleMonerisPostback(msg);
            }
        };

        this.busService.addEventListener('notification', this._onNotif);

        onMounted(() => {
            // Optional: mark a Moneris line as pending visually
            const pending = this.currentOrder?.paymentlines?.find(
                (pl) => pl.payment_method?.use_payment_terminal === "moneris"
                    && !pl.is_done()
            );
            if (pending && pending.get_payment_status() !== "pending") {
                pending.set_payment_status("pending");
            }
        });

        onWillUnmount(() => {
            if (this._onNotif) this.busService.removeEventListener('notification', this._onNotif);
            if (this.channel) this.busService.deleteChannel(this.channel);
        });
    },

    _handleMonerisPostback(msg) {
        if (!msg) return;
        const order = this.currentOrder;
        if (!order) return;

        // Match order id; adapt if your orderId mapping differs
        const candidates = [order.name, order.uid, order.server_id];
        if (msg.orderId && !candidates.includes(msg.orderId)) {
            return;
        }

        const pl = order.paymentlines?.find(
            l => l.payment_method?.use_payment_terminal === "moneris" && !l.is_done()
        );
        if (!pl) return;

        if (msg.approved) {
            pl.set_payment_status("done");
            const term = pl.payment_method?.payment_terminal;
            if (term?.paymentNotificationResolver) {
                term.paymentNotificationResolver(true);
                term.paymentNotificationResolver = null;
            }
            if (order.is_paid && order.is_paid()) {
                this.validateOrder(true);
            }
            this.notification.add(this.env._t("Moneris payment approved."), { type: "info" });
        } else if (msg.completed) {
            pl.set_payment_status("rejected");
            const term = pl.payment_method?.payment_terminal;
            if (term?.paymentNotificationResolver) {
                term.paymentNotificationResolver(false);
                term.paymentNotificationResolver = null;
            }
            const reason = msg.responseCode ? ` (code ${msg.responseCode})` : "";
            this.notification.add(this.env._t("Moneris payment declined") + reason, { type: "danger", sticky: true });
        }
    },
});

/** @odoo-module **/

import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";
import { onMounted, onWillUnmount } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";

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

        if (msg.type === 'sync_success') {
            this.notification.add(_t("Moneris terminal synced successfully."), { type: "info" });
            return;
        } else if (msg.type === 'sync_failed') {
            const reason = msg.statusCode ? ` (code ${msg.statusCode})` : "";
            this.notification.add(_t("Moneris terminal sync failed") + reason, { type: "danger", sticky: true });
            return;
        } else if (msg.type === 'terminal_error' || (msg.status && String(msg.status).toLowerCase().includes('error'))) {
            const ed = Array.isArray(msg.errorDetails) && msg.errorDetails.length ? `: ${msg.errorDetails[0].issue || msg.errorDetails[0].errorCode}` : '';
            const code = msg.statusCode ? ` (code ${msg.statusCode})` : '';
            this.notification.add(_t("Moneris terminal error") + ed + code, { type: "danger", sticky: true });
            return;
        } else if (msg.approved) {
            pl.set_payment_status("done");
            const term = pl.payment_method?.payment_terminal;
            if (term?.paymentNotificationResolver) {
                term._clearCancelTimer?.();
                term.paymentNotificationResolver(true);
                term.paymentNotificationResolver = null;
            }
            try { delete pl.moneris_started_at; } catch (e) {}
            // Avoid re-entrant order validation while POS is flushing
            this.notification.add(_t("Moneris payment approved."), { type: "info" });
        } else if (msg.completed) {
            pl.set_payment_status("rejected");
            const term = pl.payment_method?.payment_terminal;
            if (term?.paymentNotificationResolver) {
                term._clearCancelTimer?.();
                term.paymentNotificationResolver(false);
                term.paymentNotificationResolver = null;
            }
            try { delete pl.moneris_started_at; } catch (e) {}
            const reason = msg.responseCode ? ` (code ${msg.responseCode})` : "";
            this.notification.add(_t("Moneris payment declined") + reason, { type: "danger", sticky: true });
        }
    },
});

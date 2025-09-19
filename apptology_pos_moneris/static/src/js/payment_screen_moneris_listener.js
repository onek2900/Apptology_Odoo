/** @odoo-module **/

import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";
import { onMounted, onWillUnmount } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";

patch(PaymentScreen.prototype, {
    setup() {
        super.setup(...arguments);
        this.busService = this.env.services.bus_service;
        this.monerisChannel = `pos_moneris_${this.pos.config.id}`;
        this.busService.addChannel(this.monerisChannel);

        this._onNotif = ({ detail: notifications }) => {
            const events = notifications.filter(n => (n.payload?.channel === this.monerisChannel) || n.payload === 'MONERIS_LATEST_RESPONSE');
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
            if (this.monerisChannel) this.busService.deleteChannel(this.monerisChannel);
        });
    },

    _handleMonerisPostback(msg) {
        if (!msg) return;
        const order = this.currentOrder;
        if (!order) return;

        // Ignore sync messages on the payment screen; navbar handles them.
        if (msg.type === 'sync_success' || msg.type === 'sync_failed' || msg.action === 'sync') {
            return;
        }

        // Require orderId to match this order to affect payment lines
        if (!msg.orderId) return;
        const candidates = [order.name, order.uid, order.server_id];
        if (!candidates.includes(msg.orderId)) {
            return;
        }

        const pl = order.paymentlines?.find(
            (l) => l.payment_method?.use_payment_terminal === "moneris" && !l.is_done()
        );
        if (!pl) return;

        // Only act on purchase outcomes
        if (msg.type === 'terminal_error' || (msg.status && String(msg.status).toLowerCase().includes('error'))) {
            const ed = Array.isArray(msg.errorDetails) && msg.errorDetails.length ? `: ${msg.errorDetails[0].issue || msg.errorDetails[0].errorCode}` : '';
            const code = msg.statusCode ? ` (code ${msg.statusCode})` : '';
            this.notification.add(_t("Moneris terminal error") + ed + code, { type: "danger", sticky: true });
            return;
        } else if (msg.type === 'purchase' && msg.approved) {
            pl.set_payment_status("done");
            const term = pl.payment_method?.payment_terminal;
            if (term?.paymentNotificationResolver) {
                term._clearCancelTimer?.();
                term.paymentNotificationResolver(true);
                term.paymentNotificationResolver = null;
            }
            try { delete pl.moneris_started_at; } catch (e) {}
            this.notification.add(_t("Moneris payment approved."), { type: "info" });
        } else if (msg.type === 'purchase' && String(msg.statusCode || '').trim() === '5220') {
            pl.set_payment_status("retry");
            const term = pl.payment_method?.payment_terminal;
            if (term?.paymentNotificationResolver) {
                term._clearCancelTimer?.();
                term.paymentNotificationResolver(false);
                term.paymentNotificationResolver = null;
            }
            try { delete pl.moneris_started_at; } catch (e) {}
            this.notification.add(_t("Moneris payment cancelled on terminal."), { type: "info" });
        } else if (msg.type === 'purchase' && msg.completed) {
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

/** @odoo-module */

import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";
import { onMounted, onWillUnmount } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";

patch(PaymentScreen.prototype, {
    setup() {
        super.setup(...arguments);
        this.orm = useService("orm");
        onMounted(() => {
            const pendingPaymentLine = this.currentOrder.paymentlines.find(
                (paymentLine) =>
                    paymentLine.payment_method.use_payment_terminal ===
                        "moneris" &&
                    !paymentLine.is_done() &&
                    paymentLine.get_payment_status() !== "pending"
            );
            if (pendingPaymentLine) {
                pendingPaymentLine.set_payment_status("retry");
            }
            // start a light ticker to refresh controls while waiting
            this._monerisCancelTicker = setInterval(() => {
                const pl = this.currentOrder?.paymentlines?.find(
                    (l) => l.payment_method?.use_payment_terminal === 'moneris' && !l.is_done()
                );
                if (pl && pl.moneris_started_at) {
                    this.render(true);
                }
            }, 1000);
        });

        onWillUnmount(() => {
            if (this._monerisCancelTicker) {
                clearInterval(this._monerisCancelTicker);
                this._monerisCancelTicker = null;
            }
        });
    },

    get controlButtons() {
        const buttons = super.controlButtons || [];
        buttons.push({
            name: "moneris_sync",
            text: _t("Sync Moneris"),
            action: () => this._monerisManualSync(),
            sequence: 5,
        });
        // Contextual Cancel button (appears after 5s of waiting)
        const pl = this.currentOrder?.paymentlines?.find(
            (l) => l.payment_method?.use_payment_terminal === 'moneris' && !l.is_done()
        );
        if (pl && pl.moneris_started_at && Date.now() - pl.moneris_started_at >= 5000) {
            buttons.push({
                name: "moneris_cancel",
                text: _t("Cancel Moneris"),
                action: () => {
                    const term = pl.payment_method?.payment_terminal;
                    term?.send_payment_cancel?.();
                },
                sequence: 6,
                isHighlighted: true,
            });
        }
        return buttons;
    },

    async _monerisManualSync() {
        try {
            const cfgId = this.pos.config.id;
            const sessionId = this.pos?.pos_session?.id || this.currentOrder?.pos_session_id;
            await this.orm.silent.call(
                "pos.payment.method",
                "action_moneris_sync_now_for_config",
                [cfgId, sessionId]
            );
            this.notification.add(_t("Moneris sync requested"), { type: "info" });
        } catch (e) {
            this.notification.add(_t("Failed to request Moneris sync"), { type: "danger" });
        }
    },
});

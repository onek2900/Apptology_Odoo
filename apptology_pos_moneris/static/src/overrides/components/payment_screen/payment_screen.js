/** @odoo-module */

import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";
import { onMounted, onWillUnmount } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";

patch(PaymentScreen.prototype, {
    setup() {
        super.setup(...arguments);
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

    
});

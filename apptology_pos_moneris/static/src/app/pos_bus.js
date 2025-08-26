/** @odoo-module */
import { patch } from "@web/core/utils/patch";
import { PosBus } from "@point_of_sale/app/bus/pos_bus_service";

patch(PosBus.prototype, {
    dispatch(message) {
        super.dispatch(...arguments);

        if (message.type === "MONERIS_LATEST_RESPONSE") {
            const pendingLine = this.pos.getPendingPaymentLine("moneris");
            if (!pendingLine) {
                return;
            }

            const paymentMethod = pendingLine.payment_method;
            if (!paymentMethod) {
                return;
            }

            const terminal = paymentMethod.payment_terminal;
            if (!terminal || !terminal.paymentNotificationResolver) {
                return;
            }

            if (pendingLine) {
                pendingLine.payment_method.payment_terminal.handleMonerisStatusResponse();
            }
        }
    },
});

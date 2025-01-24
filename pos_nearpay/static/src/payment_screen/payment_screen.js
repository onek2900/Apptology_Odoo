/** @odoo-module **/

import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";

patch(PaymentScreen.prototype, {
    //@override
    async sendPaymentCancel(line) {
        const payment_terminal = line.payment_method.payment_terminal;
        line.set_payment_status("waitingCancel");
        const isCancelSuccessful = await payment_terminal.send_payment_cancel(
            this.currentOrder,
            line.cid
        );
        if (isCancelSuccessful) {
            if (line.payment_method.use_payment_terminal !== 'NRP') line.set_payment_status("retry");
        } else {
            line.set_payment_status("waitingCard");
        }
    }
});
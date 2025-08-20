/** @odoo-module */
import { patch } from "@web/core/utils/patch";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";

patch(PaymentScreen.prototype, {
    async validateOrder(isForceValidate) {
        if ($("#payment_note_textarea") && $("#payment_note_textarea")[0]) {
            this.pos.get_order().set_global_note($("#payment_note_textarea")[0].value);
        }
        return await super.validateOrder(...arguments);
    },
    
});

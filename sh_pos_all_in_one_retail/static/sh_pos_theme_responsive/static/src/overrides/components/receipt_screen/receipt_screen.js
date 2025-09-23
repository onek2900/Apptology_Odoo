/** @odoo-module */

import { ReceiptScreen } from "@point_of_sale/app/screens/receipt_screen/receipt_screen";
import { patch } from "@web/core/utils/patch";

patch(ReceiptScreen.prototype, {
    async setup(){
      await  super.setup()
      
    },
    async onDisplaySendEmail() {
        if ($('.send-email').hasClass('hide_send_mail')) {
            $('.send-email').removeClass('hide_send_mail');
        } else {
            $('.send-email').addClass('hide_send_mail');
        }

    }
});

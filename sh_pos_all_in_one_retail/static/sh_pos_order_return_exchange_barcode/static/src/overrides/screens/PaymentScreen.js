/** @odoo-module */

import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";

// patch(PaymentScreen.prototype, {
//     async validateOrder(isForceValidate) {
//         await super.validateOrder(...arguments);
//         var self = this;
//         this.currentOrder['barcode'] = this.currentOrder.name
//         if (this.currentOrder.get_partner()) {
//             this.currentOrder['partner_id'] = this.currentOrder.get_partner().id
//         } else {
//             this.currentOrder['partner_id'] = false
//         }
//         let Lines = []
//         for (let line of this.currentOrder.orderlines) {
//             let newline = line.export_as_JSON()
//             newline["sh_return_qty"] = 0
//             Lines.push(newline)
//         }
//         this.pos.db.order_by_barcode[this.currentOrder.name.split(' ')[1]] = [this.currentOrder.export_as_JSON(), Lines];
//     },
// });

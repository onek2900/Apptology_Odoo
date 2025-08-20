/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { TicketScreen } from "@point_of_sale/app/screens/ticket_screen/ticket_screen";
import { patch } from "@web/core/utils/patch";

patch(TicketScreen.prototype, {
  onClickOrder(clickedOrder) {
    super.onClickOrder(clickedOrder);
    // if (!clickedOrder || clickedOrder.locked) {
    //   var order = clickedOrder;
    //   var self = this;
    //   if ( order.name && (this.pos.config.sh_pos_order_number || this.pos.config.sh_pos_receipt_invoice)) {
    //     let Orders = this.orm.call(
    //       "pos.order",
    //       "search_read",
    //       [[["pos_reference", "=", order.name]]],
    //       { name: order.name, account_move: order.account_move }
    //     );
    //     if (Orders && Orders.length > 0) {
    //       if (
    //         Orders[0] &&
    //         Orders[0]["name"] &&
    //         this.pos.config.sh_pos_order_number
    //       ) {
    //         order["pos_recept_name"] = Orders[0]["name"];
    //       }
    //       if (
    //         Orders[0] &&
    //         Orders[0]["account_move"] &&
    //         this.pos.config.sh_pos_receipt_invoice
    //       ) {
    //         var invoice_number = Orders[0]["account_move"][1].split(" ")[0];
    //         order["invoice_number"] = invoice_number;
    //       }
    //     }
    //   }
    // } else {
    //   this._setOrder(clickedOrder);
    // }
  },
});

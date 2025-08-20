/** @odoo-module **/

import { OrderReceipt } from "@point_of_sale/app/screens/receipt_screen/receipt/order_receipt";
import { patch } from "@web/core/utils/patch";
import { usePos } from "@point_of_sale/app/store/pos_hook";


patch(OrderReceipt.prototype, {
  setup() {
    this.props['receipt_type'] = ""
    super.setup();
    this.pos = usePos();
    if (!this.pos.config.sh_enable_product_code_in_receipt) {
      $("#test_1").hide();
    }
    this.receipt_type = this.props.receipt_type ? this.props.receipt_type : 'standard'
  },
});

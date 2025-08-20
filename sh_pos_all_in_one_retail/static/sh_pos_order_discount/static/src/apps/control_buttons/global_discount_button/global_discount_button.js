/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { GlobalDiscountPopupWidget } from "@sh_pos_all_in_one_retail/static/sh_pos_order_discount/apps/popups/global_discount_popup/global_discount_popup";

export class GlobalDiscountButton extends Component {
  static template = "sh_pos_all_in_one_retail.GlobalDiscountButton";
  setup() {
    this.pos = usePos();
    this.popup = useService("popup");
  }
  async onClick() {
    if (
      this.pos.get_order().get_orderlines() &&
      this.pos.get_order().get_orderlines().length > 0
    ) {
      this.pos.is_global_discount = true;
      let { confirmed, payload } = this.popup.add(GlobalDiscountPopupWidget);
      if (confirmed) {
        return true;
      } else {
        return;
      }
    } else {
      alert("Add Product In Cart.");
    }
  }
}

ProductScreen.addControlButton({
  component: GlobalDiscountButton,
  condition: function () {
    return this.pos.config.sh_allow_global_discount;
  },
});

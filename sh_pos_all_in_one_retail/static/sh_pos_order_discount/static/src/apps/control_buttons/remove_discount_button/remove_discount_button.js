/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";

export class RemoveDiscountButton extends Component {
  static template = "sh_pos_all_in_one_retail.RemoveDiscountButton";
  setup() {
    this.pos = usePos();
    this.popup = useService("popup");
  }
  async onClick() {
    var orderlines = this.pos.get_order().get_orderlines();
    if (orderlines) {
      for (let each_orderline of orderlines) {
        each_orderline.set_discount(0);
        each_orderline.set_global_discount(0);
      }
      this.pos.get_order().set_order_global_discount(0.0);
    }
  }
}

ProductScreen.addControlButton({
  component: RemoveDiscountButton,
  condition: function () {
    return (
      this.pos.config.sh_allow_global_discount ||
      this.pos.config.sh_allow_order_line_discount
    );
  },
});

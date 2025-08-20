/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { OrderTypePopup } from "@sh_pos_all_in_one_retail/static/sh_pos_order_type/apps/popups/order_type_popup/order_type_popup"

export class OrderTypeButton extends Component {
  static template = "sh_pos_order_type.OrderTypeButton";
  setup() {
    super.setup(...arguments)
    this.pos = usePos();
    this.popup = useService("popup");
  }
  async onClickOrderTypeBtn() {
    await this.popup.add(OrderTypePopup); 
    this.render()
  }
}

ProductScreen.addControlButton({
  component: OrderTypeButton,
  condition: function () {
    return this.pos.config.enable_order_type && this.pos.config.order_type_mode;
  },
});

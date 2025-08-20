/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { GlobalDiscountPopupWidget } from "@sh_pos_all_in_one_retail/static/sh_pos_order_discount/apps/popups/global_discount_popup/global_discount_popup";


patch(ProductScreen.prototype, {
  setup() {
    super.setup(...arguments);
    this.popup = useService("popup");
  },
  onNumpadClick(buttonValue) {
    super.onNumpadClick(buttonValue);
    var self = this;
    if (
      buttonValue &&
      buttonValue == "discount" &&
      self.pos.config.sh_allow_order_line_discount
    ) {
      self.pos.is_global_discount = false;
      let { confirmed } = this.popup.add(GlobalDiscountPopupWidget);
      if (confirmed) {
      } else {
        return;
      }
    }
  },
  _setValue(val) {
    // super._setValue(val);
    var mode = this.pos.numpadMode;
    var order = this.pos.get_order();
    if (order.get_selected_orderline() && this.pos.config.sh_allow_order_line_discount) {
      if (mode == "discount") {
        if (val){
          order.get_selected_orderline().set_discount(0);
          var sh_dic = order.get_selected_orderline().get_global_discount()
          sh_dic = parseFloat(sh_dic).toFixed(2)
          order.get_selected_orderline().set_discount(0);
          var price = order.get_selected_orderline().get_display_price();
          var current_price = (price * val) / 100;
          var discount = ((order.get_selected_orderline().get_display_price() * order.get_selected_orderline().quantity - current_price) / (order.get_selected_orderline().price * order.get_selected_orderline().quantity)) * 100;
          discount = discount.toFixed(2)
          order.get_selected_orderline().set_discount(discount);
        }else{
          // debugger;
          // var get_global_discount = parseFloat(this.pos.get_order().get_order_global_discount())
          // var amount = order.get_selected_orderline().price - (order.get_selected_orderline().get_discount() / 100)
          // var set_disocunt = get_global_discount - amount
          // console.log('set_disocunt-->',set_disocunt);
          this.pos.get_order().set_order_global_discount(0.00)
          super._setValue(...arguments)
        }
      }else{
        super._setValue(val);
      }
    }else{
      super._setValue(val);
    }
}
});

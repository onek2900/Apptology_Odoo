/** @odoo-module */

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { Order, Orderline } from "@point_of_sale/app/store/models";
import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { formatFloat } from "@web/core/utils/numbers";

patch(PosStore.prototype, {
    // @Override
    async _processData(loadedData) {
        await super._processData(...arguments);
        this.is_global_discount = false;
    },
});

patch(Order.prototype, {
  setup() {
    super.setup(...arguments);
    this.order_global_discount;
  },
  set_order_global_discount(discount) {
    this.order_global_discount = discount;
  },
  get_order_global_discount() {
    return this.order_global_discount || false;
  },
});

patch(Orderline.prototype, {
  setup(_defaultObj, options) {
    super.setup(...arguments);
    this.global_discount;
    this.fix_discount;
    this.total_discount;

    if (this.order.get_orderlines().length == 0) {
      this.order.set_order_global_discount(0.0);
    }
  },
  set_global_discount(global_discount) {
    this.global_discount = global_discount;
  },
  get_global_discount() {
    return this.global_discount;
  },
  set_fix_discount(discount) {
    this.fix_discount = discount;
  },
  get_fix_discount() {
    return this.fix_discount;
  },
  get_sh_discount_str() {
    return this.discount.toFixed(2);
  },
  set_total_discount(discount) {
    this.total_discount = discount;
  },
  get_total_discount() {
    return this.total_discount || false;
  },
  set_custom_discount(discount) {
    var disc = Math.min(Math.max(discount || 0, 0), 100);
    this.discount = disc;
    this.discountStr = "" + formatFloat(disc, { digits: [69, 2] });
  },
});

/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { useService } from "@web/core/utils/hooks";

export class OrderTypePopup extends AbstractAwaitablePopup {
  static template = "sh_pos_order_discount.OrderTypePopup";
  setup() {
    super.setup();
    this.pos = usePos();
    this.popup = useService("popup");
  }
  onClickOrderType(id) {
    let ordertypes = Object.values(this.pos.order_types);
    const res = ordertypes.filter((type) => type.id == id)[0];
    if (this.pos.get_order().current_order_type == res) {
      this.pos.get_order().current_order_type = null;
    } else {
  
      this.pos.get_order().current_order_type = res;
      this.pos.get_order().current_order_type.is_home_delivery
        ? (this.displayWarning = true)
        : (this.displayWarning = false);
      this.isSelected = true;
    }
    this.render(true);
  }
  async applyChanges() {
      if (
        this.pos.get_order().current_order_type &&
        !this.pos.get_order().current_order_type.is_home_delivery
      ) {
        this.cancel();
      } else if (
        this.pos.get_order().current_order_type &&
        this.pos.get_order().current_order_type.is_home_delivery
      ) {
        this.cancel();
        const currentPartner = this.pos.get_order().get_partner();
        const { confirmed, payload: newPartner } = await this.pos.showTempScreen("PartnerListScreen", {
          partner: currentPartner,
      });
        if (confirmed) {
          this.pos.get_order().set_partner(newPartner);
          this.pos.get_order().updatePricelistAndFiscalPosition(newPartner);
        }
      } else {
          this.popup.add(ErrorPopup, {
            title: "Select order type",
            body: "Please select order type to continue......",
        });
      }
    
  }
  close() {
    this.pos.get_order().current_order_type = null;
    this.cancel();
  }
  getImg(id) {
    return `/web/image?model=sh.order.type&id=${id}&field=img`;
  }
}

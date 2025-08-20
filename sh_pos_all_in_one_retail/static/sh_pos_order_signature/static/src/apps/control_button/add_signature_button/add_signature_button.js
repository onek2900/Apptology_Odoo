/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { TemplateAddSignaturePopupWidget } from "@sh_pos_all_in_one_retail/static/sh_pos_order_signature/apps/popups/template_add_signature_popup/template_add_signature_popup";

export class AddSignatureButton extends Component {
  static template = "sh_pos_all_in_one_retail.AddSignatureButton";
  setup() {
    this.pos = usePos();
    this.popup = useService("popup");
  }
   async onClick() {
    let { confirmed } = await this.popup.add(TemplateAddSignaturePopupWidget);
    if (confirmed) {
    } else {
        return;
    }
}
}

ProductScreen.addControlButton({
  component: AddSignatureButton,
  condition: function () {
    return this.pos.config.sh_enable_order_signature;
  },
});

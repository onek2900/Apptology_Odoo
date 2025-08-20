  /** @odoo-module **/

  import { _t } from "@web/core/l10n/translation";
  import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
  import { useService } from "@web/core/utils/hooks";
  import { Component } from "@odoo/owl";
  import { usePos } from "@point_of_sale/app/store/pos_hook";
  import { TransactionPopupWidget } from "@sh_pos_all_in_one_retail/static/sh_pos_cash_in_out/app/Popups/TransactionPopupWidget/TransactionPopupWidget";
  
  export class PaymentsButton extends Component {
      static template = "sh_pos_cash_in_out.PaymentsButton";
      setup() {
          this.pos = usePos();
          this.popup = useService("popup");
        }
        async onClick() {
            let { confirmed } = await  this.popup.add(TransactionPopupWidget);
            if (confirmed) {
            } else {
                return;
            }
        }
   
  }

  ProductScreen.addControlButton({
    component: PaymentsButton,
    condition: function () {
        return this.pos.config.sh_enable_payment;
    },
});

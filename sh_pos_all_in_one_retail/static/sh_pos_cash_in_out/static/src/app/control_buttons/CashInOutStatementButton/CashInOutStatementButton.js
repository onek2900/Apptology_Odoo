  /** @odoo-module **/

  import { _t } from "@web/core/l10n/translation";
  import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
  import { useService } from "@web/core/utils/hooks";
  import { Component } from "@odoo/owl";
  import { usePos } from "@point_of_sale/app/store/pos_hook";
  import { CashInOutOptionStatementPopupWidget } from "@sh_pos_all_in_one_retail/static/sh_pos_cash_in_out/app/Popups/CashInOutOptionStatementPopupWidget/CashInOutOptionStatementPopupWidget";

  export class CashInOutStatementButton extends Component {
      static template = "sh_pos_cash_in_out.CashInOutStatementButton";
      setup() {
          this.pos = usePos();
          this.popup = useService("popup");
        }
        async onClick() {
            let { confirmed } = await  this.popup.add(CashInOutOptionStatementPopupWidget);
            if (confirmed) {
            } else {
                return;
            }
        }
   
  }

  ProductScreen.addControlButton({
      component: CashInOutStatementButton,
      condition: function () {
          return this.pos.config.sh_enable_cash_in_out_statement
      },
  })

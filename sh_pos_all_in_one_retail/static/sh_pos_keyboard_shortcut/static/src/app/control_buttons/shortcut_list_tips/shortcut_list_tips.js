  /** @odoo-module **/

  import { _t } from "@web/core/l10n/translation";
  import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
  import { useService } from "@web/core/utils/hooks";
  import { Component } from "@odoo/owl";
  import { usePos } from "@point_of_sale/app/store/pos_hook";
  import { ShortcutTipsPopup } from "@sh_pos_all_in_one_retail/static/sh_pos_keyboard_shortcut/app/popups/shortcut_tips_popup/shortcut_tips_popup";
  
  export class ShortcutListTips extends Component {
      static template = "sh_pos_all_in_one_retail.ShortcutListTips";
      setup() {
          this.pos = usePos();
          this.popup = useService("popup");
        }
        async onClick() {
            let { confirmed } = await  this.popup.add(ShortcutTipsPopup);
            if (confirmed) {
            } else {
                return;
            }
        }
   
  }

  ProductScreen.addControlButton({
      component: ShortcutListTips,
      condition: function () {
          return this.pos.config.sh_enable_shortcut
      },
  })

  /** @odoo-module **/

    import { _t } from "@web/core/l10n/translation";
    import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
    import { useService } from "@web/core/utils/hooks";
    import { Component } from "@odoo/owl";
    import { usePos } from "@point_of_sale/app/store/pos_hook";
    import { LabelPopup } from "@sh_pos_all_in_one_retail/static/sh_pos_order_label/app/labal_popup/labal_popup"

    export class AddlabelButton extends Component {
        static template = "sh_pos_order_label.AddlabelButton";
        setup() {
            this.pos = usePos();
            this.popup = useService("popup");
        }
        onclickLabelBtn() {
            this.popup.add(LabelPopup)
        }
    }

    ProductScreen.addControlButton({
        component: AddlabelButton,
        condition: function () {
            return this.pos.config.enable_order_line_label
        },
    })

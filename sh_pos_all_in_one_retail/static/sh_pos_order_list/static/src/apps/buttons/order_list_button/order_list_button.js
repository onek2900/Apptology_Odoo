/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";

export class Orderlistbutton extends Component {
    static template = "sh_pos_order_list.Orderlistbutton";

    setup() {
        this.pos = usePos();
        this.popup = useService("popup");
    }
    async onClick() {
        await this.pos.showScreen("OrderListScreen",);
    }
}
ProductScreen.addControlButton({
    component: Orderlistbutton,
    condition: function () {
        return this.pos.config.sh_enable_order_list;
    }
});

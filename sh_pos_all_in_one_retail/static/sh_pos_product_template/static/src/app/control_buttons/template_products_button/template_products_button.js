/** @odoo-module */

import { usePos } from "@point_of_sale/app/store/pos_hook";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { Component } from "@odoo/owl";

export class TemplateProductsButton extends Component {
    static template = "sh_pos_all_in_one_retail.TemplateProductsButton";

    setup() {
        super.setup();
        this.pos = usePos();
    }
    async onClickTemplateLoad(){
        const { confirmed, payload } = await this.pos.showTempScreen("TemplateProductsListScreenWidget");
        if (confirmed) {
        }
    }
}

ProductScreen.addControlButton({
    component: TemplateProductsButton,
    condition: function () {
        return this.pos.config.sh_enable_product_template;
    },
});

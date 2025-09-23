/** @odoo-module */

import { Component } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";

export class ProductListItem extends Component {
    static template = "sh_pos_theme_responsive.ProductListItem";
    setup() {
        super.setup(...arguments);
        this.pos = usePos();
        
    }
}

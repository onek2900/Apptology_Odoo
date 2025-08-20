/** @odoo-module **/

import { registry } from "@web/core/registry";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { Component } from "@odoo/owl";

export class TemplateProductsLine extends Component {
    static template = "sh_pos_all_in_one_retail.TemplateProductsLine";
    static props = {
        onClick: { type: Function, optional: true },}
        
    setup() {
        this.pos = usePos();
    }
    get highlight() {
        return this.props.template !== this.props.selectedTemplate ? "" : "highlight";
    }
  
}
registry.category("pos_screens").add("TemplateProductsLine", TemplateProductsLine);

/** @odoo-module **/

import { registry } from "@web/core/registry";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { Component } from "@odoo/owl";
import { TemplateProductsLine } from "@sh_pos_all_in_one_retail/static/sh_pos_product_template/app/screen/template_products_line/template_products_line";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { useService } from "@web/core/utils/hooks";
import { useDebounced } from "@web/core/utils/timing";

export class TemplateProductsListScreenWidget extends Component {
    static template = "sh_pos_all_in_one_retail.TemplateProductsListScreenWidget";
    static components = { TemplateProductsLine };

    setup() {
        this.pos = usePos();
        this.popup = useService("popup");
        console.log("props ==>", this.props);
        this.state = {
            query: null,
            selectedTemplate: this.props.template,
        };
    
        this.updateTemplateList = useDebounced(this.updateTemplateList, 70);
    }
    get_all_product_templates() {
        return this.pos.pos_product_templates;
    }
    updateTemplateList(event) {
        this.state.query = event.target.value;
        const templatelistcontents = this.templatelistcontents;
        if (event.code === "Enter" && templatelistcontents.length === 1) {
            this.state.selectedTemplate = templatelistcontents[0];
        } else {
            this.render();
        }
    }
    get_template_by_name(name) {
        var templates = this.get_all_product_templates();
        return templates.filter((template) =>{
            if (template["name"]) {
                if (template["name"].indexOf(name) > -1) {
                    return true;
                } else {
                    return false;
                }
            }
        });
    }

    get templatelistcontents() {
        if (this.state.query && this.state.query.trim() !== "") {
            var templates = this.get_template_by_name(this.state.query.trim());
            return templates;
        } else {
            var templates = this.get_all_product_templates();
            return templates;
        }
    }
    back() {
        if (this.state.detailIsShown && !force) {
            this.state.detailIsShown = false;
        } else {
            this.props.resolve({ confirmed: false, payload: false });
            this.pos.closeTempScreen();
        }
    }
    get currentOrder() {
        return this.pos.get_order();
    }

    async LoadTemplate(event) {
        var self = this;
        
        if (this.state.selectedTemplate) {
            var selectedTemplateId = this.state.selectedTemplate["id"];
            var template_lines = this.pos.template_line_by_id[selectedTemplateId];
            
            var order = this.currentOrder;
            if (template_lines.length) {
                for(let line of template_lines){
                    var product_id = line.name ? line.name : false;
                    if (product_id) {
                        var product = self.pos.db.get_product_by_id(product_id);
                        if (product) {
                            order.add_product(product, {
                                quantity: line.ordered_qty,
                                price: line.unit_price,
                                discount: line.discount,
                            });
                            order.get_selected_orderline().is_template_product = true
                            order.get_selected_orderline().template_price = line.unit_price
                        }
                    }
                }
            }
            this.pos.closeTempScreen();
        } else {
            this.popup.add(ErrorPopup, {
                title:  ' ',
                body: 'Please Select Template',
            })
        }
    }
    clickLine(temp) {
        let template = temp
        if (this.state.selectedTemplate === template) {
            this.state.selectedTemplate = null;
        } else {
            this.state.selectedTemplate = template;
        }
        this.render();
    }
  
}
registry.category("pos_screens").add("TemplateProductsListScreenWidget", TemplateProductsListScreenWidget);
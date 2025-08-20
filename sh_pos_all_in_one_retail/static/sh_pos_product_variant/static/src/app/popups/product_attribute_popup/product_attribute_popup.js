/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
import { VariantProductItem } from "@sh_pos_all_in_one_retail/static/sh_pos_product_variant/app/VariantProductItem/VariantProductItem";
import { usePos } from "@point_of_sale/app/store/pos_hook";


export class ProductAttributePopup extends AbstractAwaitablePopup {
    static components = { VariantProductItem };
    static template = "sh_pos_all_in_one_retail.ProductAttributePopup";
    setup() {
        super.setup();
        this.product_varaints = []
        this.pos = usePos()
        this.selected_product = null;
        this.selected_attribute = this.props.attribute_by_id;
        this.attribute_product = false;
    }
    get getAttribute_lines() {
        return this.props.attribute_lines
    }
    async getPayload() {
        return this.selected_product;
    }
    get showAlternativeProducts() {
        return this.pos.config.sh_pos_display_alternative_products
    }
    get VariantProductToDisplay() {
        if (this.productFilter && this.productFilter.length > 0) {
            return this.productFilter
        } else {
            return this.props.product_variants;
        }
    }
    confirm(){
        const product = this.selected_product
        if ( this.pos.config.sh_close_popup_after_single_selection ){   
            if (product){
                this.pos.addProductToCurrentOrder(product)
                super.confirm()
            }
        }else{
            if (product){
                this.pos.addProductToCurrentOrder(product) 
            }
        }
    }
    clickProduct(product) {
        if(product){
            this.pos.addProductToCurrentOrder(product)
        }
    }
    get getAlternativeProduct(){
        return this.props.alternative_products
    }
    selectAttributeValue(event) {
        let attribute_id = $(event.target).parent().attr('attribute_line_id')
        let att_value_id = $(event.target).attr('att_value_id')

        $(event.target).parent().find('.sh_att_value').removeClass('sh_highlight')
        $(event.target).addClass('sh_highlight')
        this.selected_attribute[parseInt(attribute_id)] = parseInt(att_value_id)
        this.find_varaint()
    }
    find_varaint(){
        let selected_attributes = Object.values(this.selected_attribute)

        let variant_ids = this.props.varaint_ids;
        var sh_product = false
        for (let varinat_id of variant_ids) {
            let product = varinat_id            
            if(product.product_template_attribute_value_ids.toString() === selected_attributes.toString()){
                sh_product = product
            }
        }
        // return sh_product
        this.selected_product = sh_product
    }
    async on_click_show_qty(){
        var product = this.selected_product

        this.pos.showStock(product.id)

    }
}
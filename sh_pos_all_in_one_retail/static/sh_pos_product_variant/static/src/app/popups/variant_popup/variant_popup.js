/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
import { VariantProductItem } from "@sh_pos_all_in_one_retail/static/sh_pos_product_variant/app/VariantProductItem/VariantProductItem";
import { usePos } from "@point_of_sale/app/store/pos_hook";


export class VariantPopup extends AbstractAwaitablePopup {
    static components = { VariantProductItem };
    static template = "sh_pos_all_in_one_retail.VariantPopup";
    setup() {
        super.setup();
        this.product_varaints = []
        this.pos = usePos()
    }
    get shClasses(){
        var classes = ''

        if( this.VariantProductToDisplay.length < 6 ){
            classes = "sh_lessthen_6_varaint"
        }else if( this.VariantProductToDisplay.length >= 6 && this.VariantProductToDisplay.length < 15 ){
            classes = "sh_lessthen_15_varaint"
        }else{
            classes = "sh_morethan_15_variant"
        }

        return classes
    }
    get getAlternativeProduct(){
        return this.props.alternative_products || []
    }
    get showAlternativeProducts() {
        return this.pos.config.sh_pos_display_alternative_products
    }
    clickProduct(product) {
        if(product){
            this.pos.addProductToCurrentOrder(product)
            if (this.pos.config.sh_close_popup_after_single_selection) {
                this.confirm()
            }
        }
    }
    get VariantProductToDisplay() {
        if (this.productFilter && this.productFilter.length > 0) {
            return this.productFilter
        } else {
            return this.props.product_variants;
        }
    }
    updateSearch(event) {
        var val = event.target.value || ""
        var searched_varaints = this.pos.db.search_variants(this.props.product_variants, val);
        if (searched_varaints && searched_varaints.length > 0) {
            this.productFilter = searched_varaints
        } else {
            this.productFilter = []
        }
        this.render()
    }
}
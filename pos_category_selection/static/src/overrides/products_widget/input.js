/** @odoo-module */
import { Input } from "@point_of_sale/app/generic_components/inputs/input/input";
import { patch } from "@web/core/utils/patch";

patch(Input.prototype, {
setValue(newValue, tModel = this.props.tModel) {
        if(!newValue){
            this.props.tModel[0].categorySelected=false
            this.props.tModel[0].subcategorySelected=false
            this.props.tModel[0].currentCategoryId=0
            this.props.tModel[0].setSelectedCategoryId(0)

        }
        else{
            this.props.tModel[0].categorySelected=true
            this.props.tModel[0].subcategorySelected=true
        }
        super.setValue(newValue, tModel);
        this.props.callback?.(newValue);
    }
    });
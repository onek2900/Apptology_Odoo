/** @odoo-module */

import { PartnerDetailsEdit } from "@point_of_sale/app/screens/partner_list/partner_editor/partner_editor";
import { patch } from "@web/core/utils/patch";

patch(PartnerDetailsEdit.prototype, {
    setup(){
        super.setup(...arguments);
        this.changes["sh_enable_max_dic"] = this.props.partner.sh_enable_max_dic || false
        this.changes["sh_maximum_discount"] = this.props.partner.sh_maximum_discount || 0
        this.changes["sh_discount_type"] = this.props.partner.sh_discount_type || false
    },   
    get show_discount_div(){
        if(this.changes.sh_enable_max_dic){
            return true
        }else{
            return false
        }
    },
    saveChanges() {
        if (this.pos.config.sh_enable_customer_discount) {
            let processedChanges = {};
            for (const [key, value] of Object.entries(this.changes)) {
                if (this.intFields.includes(key)) {
                    processedChanges[key] = parseInt(value) || false;
                } else {
                    processedChanges[key] = value;
                }
            }
            processedChanges['sh_enable_max_dic'] = this.changes.sh_enable_max_dic || false
            processedChanges['sh_maximum_discount'] = this.changes.sh_maximum_discount || false
            processedChanges['sh_discount_type'] = this.changes.sh_discount_type || false
            if ((!this.props.partner.name && !processedChanges.name) ||
                processedChanges.name === '') {
                    return this.popup.add(ErrorPopup, {
                        title: _t("A Customer Name Is Required"),
                    });
            }
            processedChanges.id = this.props.partner.id || false;
            this.props.saveChanges(processedChanges);
        }
        else {
            super.saveChanges()
        }
    }

});

/** @odoo-module */

import { PartnerListScreen } from "@point_of_sale/app/screens/partner_list/partner_list";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";

patch(PartnerListScreen.prototype, {
    setup(){
        super.setup()
        this.popup = useService("popup");
    },
    confirm() {
        if(this.pos.config.sh_pos_enable_customer_max_discount){

            var partner = this.state.selectedPartner
            if (partner && partner.sh_enable_max_dic) {
                var self = this;
                var Order = self.pos.get_order()
    
                var sh_total_after_dic = Order.get_total_with_tax()
                var sh_product_total = Order.get_total_without_tax() + Order.get_total_discount()
                var sh_customer_max_dis = partner.sh_maximum_discount
                if (partner.sh_discount_type == "percentage") {
                    var sh_customer_discount_per = ((sh_product_total - sh_total_after_dic) * 100) / sh_product_total
    
                    if (sh_customer_discount_per > sh_customer_max_dis) {
    
                        var body = "Sorry, " + sh_customer_discount_per.toFixed(2) + "% discount is not allowed. Maximum discount for this customer is " + sh_customer_max_dis + "%";
                        this.popup.add(ErrorPopup, {
                            title: 'Exceed Discount Limit !',
                            body: body,
                        })
                    } else {
                        return super.confirm()
                    }
    
                }
                else {
                    var sh_customer_discount_fixed = Order.get_total_discount()
                    if (sh_customer_discount_fixed > sh_customer_max_dis) { 
                        
                        var body = "Sorry, " + sh_customer_discount_fixed.toFixed(2) + " discount is not allowed. Maximum discount for this customer is " + sh_customer_max_dis;
                        this.popup.add(ErrorPopup, {
                            title: 'Exceed Discount Limit !',
                            body: body,
                        })
                    } else {
                        return super.confirm()
                    }
                }
    
            } else {
                return super.confirm()
            }
        } else {
            return super.confirm()
        }
    }
});




/** @odoo-module **/

import { Order, Orderline } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";

patch(Order.prototype, {
    async pay() {
        var self = this;

        var Order = self.pos.get_order()
        if (self.pos.config.sh_pos_enable_customer_max_discount) {

            if (Order && Order.get_partner()) {
                var Client = Order.get_partner()
                if (Client.sh_enable_max_dic) {
                    var sh_total_after_dic = Order.get_total_with_tax()
                    var sh_product_total = Order.get_total_with_tax() + Order.get_total_discount()
                    var sh_customer_max_dis = Client.sh_maximum_discount

                    if (Client.sh_discount_type == "percentage") {
                        var sh_customer_discount_per = ((sh_product_total - sh_total_after_dic) * 100) / sh_product_total
                        if (parseFloat(sh_customer_discount_per.toFixed(2)) > sh_customer_max_dis) {
                            var body = "Sorry, " + sh_customer_discount_per.toFixed(2) + "% discount is not allowed. Maximum discount for this customer is " + sh_customer_max_dis + "%";
                            this.env.services.popup.add(ErrorPopup,  {
                                title: 'Exceed Discount Limit !',
                                body: body,
                            })
                        }
                        else {
                            super.pay()
                        }
                    }
                    else {
                        var sh_customer_discount_fixed = Order.get_total_discount()

                        if (sh_customer_discount_fixed > sh_customer_max_dis) {
                            var body = "Sorry, " + sh_customer_discount_fixed.toFixed(2) + " discount is not allowed. Maximum discount for this customer is " + sh_customer_max_dis;
                            this.env.services.popup.add(ErrorPopup,  {
                                title: 'Exceed Discount Limit !',
                                body: body,
                            })
                        } else {
                            super.pay()
                        }
                    }
                } else {
                    super.pay()
                }
            } else {
                super.pay()
            }
        }
        else {
            super.pay()
        }

    }
})
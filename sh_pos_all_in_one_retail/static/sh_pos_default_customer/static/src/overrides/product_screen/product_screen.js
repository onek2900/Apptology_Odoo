/** @odoo-module **/

import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";

patch(ProductScreen.prototype, {
    setup() {
        super.setup();
        this.pos = usePos();
        this.pos.get_order();
        var self = this;
        var order = self.pos.get_order();
        if (!order.get_partner()) {
            if (self.pos.config.sh_enable_default_customer && self.pos.config.sh_default_customer_id && !self.pos.config.sh_enable_own_customer) {
                var set_partner = self.pos.db.get_partner_by_id(self.pos.config.sh_default_customer_id[0]);
                if (set_partner) {
                    order.set_partner(set_partner);
                }
            } else if (self.pos.config.sh_enable_default_customer && self.pos.config.sh_default_customer_id && self.pos.config.sh_enable_own_customer) {
                if (self.pos.user.role != 'manager') {
                    var set_partner = self.pos.db.get_partner_by_id(self.pos.config.sh_default_customer_id[0]);
                    if (set_partner && set_partner.sh_own_customer.includes(self.pos.user.id)) {
                        if (order.get_partner() && order.get_partner().sh_own_customer.length > 0) {
                            order.set_partner(set_partner);
                        }
                    }
                }else{
                    var set_partner = self.pos.db.get_partner_by_id(self.pos.config.sh_default_customer_id[0]);
                    if (set_partner) {
                        order.set_partner(set_partner);
                    }   
                }
            }
        }
    },
});

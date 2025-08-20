/** @odoo-module */

import { PartnerListScreen } from "@point_of_sale/app/screens/partner_list/partner_list";
import { patch } from "@web/core/utils/patch";


patch(PartnerListScreen.prototype, {
    setup() {
        super.setup();
        this.customer_list = []
    },
    get partners() {
        var self = this
        var customer_list = []
        if(this.pos.config.sh_enable_own_customer){
            if (this.state.query && this.state.query.trim() !== '') {
                if (this.customer_list && this.customer_list.length > 0) {
                    return this.pos.db.search_visible_partner(this.state.query.trim());
                } else {
                    return this.pos.db.search_partner(this.state.query.trim());
                }
            } else {
                var Partners = this.pos.db.partner_by_id
                if (self.pos.user.role != 'manager') {
                    for (let partner of Object.values(Partners)){
                        console.log('Partners=>',partner);
                        if (partner.sh_own_customer.includes(self.pos.user.id)) {
                            if (partner.sh_own_customer.length > 0) {
                                self.customer_list.push(1)
                                customer_list.push(partner)
                            }
                        }
                    }
                    if (customer_list.length > 0) {
                        return customer_list
                    }
                    else {
                        return []
                    }
                } else {
                    this.customer_list = []
                    return self.pos.db.get_partners_sorted(1000)
                }
            }
        }else{
            if (this.state.query && this.state.query.trim() !== '') {
                return this.pos.db.search_partner(this.state.query.trim());
            } else {
                return this.pos.db.get_partners_sorted(1000);
            }
        }
    }
});

/** @odoo-module */

import { PartnerListScreen } from "@point_of_sale/app/screens/partner_list/partner_list";
import { PartnerLine } from "@point_of_sale/app/screens/partner_list/partner_line/partner_line";
import { patch } from "@web/core/utils/patch";

patch(PartnerLine.prototype, {
    click_order_history_icon(){
        var customerOrders = Object.values(this.env.services.pos.db.pos_order_by_id).filter((x) => x[0].partner_id == this.props.partner.id)

        $('.button.back').click()
        this.env.services.pos.showScreen("OrderListScreen",{
            Orders: customerOrders
        });
    }
})
patch(PartnerListScreen.prototype, {
    setup(){
        super.setup(...arguments)
        this.state.editModeProps['customerOrders'] = []
    },
    /**
     * Needs to be pass the customer order in customer details screen
     * @override
     */
    activateEditMode() {
        if( this.pos.config.enable_history_on_client_detail && this.pos.config.sh_enable_order_list ){
            var customerOrders = Object.values(this.pos.db.pos_order_by_id).filter((x) => x[0].partner_id == this.state.editModeProps.partner.id)
            this.state.editModeProps.customerOrders = customerOrders
        }
        super.activateEditMode(...arguments)
    }
});


/** @odoo-module **/

import { TicketScreen } from "@point_of_sale/app/screens/ticket_screen/ticket_screen";
import { patch } from "@web/core/utils/patch";

patch(TicketScreen.prototype, {
    async _setOrder(order) {
        if (order.name.includes("Online-Order")) {
            await this.pos.load_server_data();
        }
        return super._setOrder(...arguments)
    }
});
/** @odoo-module **/

import { TicketScreen } from "@point_of_sale/app/screens/ticket_screen/ticket_screen";
import { patch } from "@web/core/utils/patch";

patch(TicketScreen.prototype, {
    // Keep default behavior; avoid extra syncs that cause transient duplicates
    async _setOrder() {
        return super._setOrder(...arguments);
    }
});

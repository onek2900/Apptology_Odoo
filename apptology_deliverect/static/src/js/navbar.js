/** @odoo-module */

import { Navbar } from "@point_of_sale/app/navbar/navbar";
import { patch } from "@web/core/utils/patch";

patch(Navbar.prototype, {
    async onClickOnlineOrder() {
        await this.pos.showScreen("OnlineOrderScreen");
    },
});

/** @odoo-module */

import { Navbar } from "@point_of_sale/app/navbar/navbar";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { useState } from "@odoo/owl";

patch(Navbar.prototype, {
    setup() {
        super.setup();
        this.state=useState({
            onlineOrderCount:0
        })
        this.onlineOrderCount();
        },
    async onClickOnlineOrder() {
        await this.pos.showScreen("OnlineOrderScreen");
    },
    async onlineOrderCount() {
        this.state.onlineOrderCount = await this.pos.get_online_orders();
    }
});

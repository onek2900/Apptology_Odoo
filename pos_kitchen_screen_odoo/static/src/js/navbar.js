/** @odoo-module */

import { Navbar } from "@point_of_sale/app/navbar/navbar";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { useState } from "@odoo/owl";

patch(Navbar.prototype, {
    setup() {
        super.setup();
        this.action = useService("action");
        this.orm = useService("orm");
        this.state=useState({
            is_config_present:false
        })
        this.check_config_present();
    },
    async check_config_present() {
        const config = await this.orm.searchRead(
                "kitchen.screen",
                [["pos_config_id", "=", this.pos.config.id]],
                []
            );
        this.state.is_config_present = config.length>0?true:false;
    },
    async openKitchenScreen() {
        this.action.doAction({
            type: "ir.actions.act_url",
            target: 'new',
            url: `/apptology_kitchen_screen?shop_id=${this.pos.config.id}`,
        });
    },

    async openOrderScreen() {
        const kitchenScreen = await this.orm.searchRead(
            "kitchen.screen",
            [
                ["pos_config_id", "=", this.pos.config.id],
            ],
            ["id"]
        );
        const kitchenScreenId = kitchenScreen[0]?.id;
        this.action.doAction({
            type: "ir.actions.act_url",
            target: 'new',
            url: `/apptology_order_screen?screen_id=${kitchenScreenId}`,
        });
    },
});
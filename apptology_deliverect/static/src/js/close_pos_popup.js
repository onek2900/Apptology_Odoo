/** @odoo-module */

import { ClosePosPopup } from "@point_of_sale/app/navbar/closing_popup/closing_popup";
import { patch } from "@web/core/utils/patch";
import { useState } from "@odoo/owl";

patch(ClosePosPopup.prototype, {
    setup() {
        super.setup();
        this.state = useState({ ...this.state, unFinalizedOrdersCount: 0 });
        this.isOrderFinalized();
    },
    async isOrderFinalized() {

        this.state.unFinalizedOrdersCount = await this.orm.searchCount(
                    "pos.order",
                    [["config_id","=",this.pos.config.id],["is_online_order", "=", true],["online_order_status",'!=',"finalized"],["order_status",
                    "!=",
                    "cancel"]]);
        var records = await this.orm.searchRead(
                    "pos.order",
                    [        ["config_id", "=", this.pos.config.id],
        ["is_online_order", "=", true],
        ["online_order_status", "=", "approved"],
        ["order_status", "!=", "cancel"]],['name','config_id','online_order_status','order_status'])
    }
});
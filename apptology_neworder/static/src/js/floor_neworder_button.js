/** @odoo-module */

import { FloorScreen } from "@pos_restaurant/app/screens/floor_screen/floor_screen";
import { patch } from "@web/core/utils/patch";

patch(FloorScreen.prototype, "apptology_neworder.floor_neworder_button", {
    onNewPickupOrder(ev) {
        try {
            ev?.stopPropagation?.();
        } catch (_) {}
        try {
            const pos = this.env?.services?.pos || this.pos;
            if (!pos) return;
            // Create a fresh order not linked to any table
            pos.add_new_order();
            // Navigate straight to the ProductScreen for pickup flow
            pos.showScreen("ProductScreen");
        } catch (e) {
            console.warn("Apptology NewOrder: failed to create pickup order", e);
        }
    },
});

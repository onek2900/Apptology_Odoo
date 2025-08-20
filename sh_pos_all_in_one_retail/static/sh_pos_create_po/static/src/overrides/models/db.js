/** @odoo-module */

import { PosDB } from "@point_of_sale/app/store/db";
import { patch } from "@web/core/utils/patch";

patch(PosDB.prototype, {
    get_all_orders: function () {
        return this.all_purchase_orders;
    },
    remove_all_purchase_orders: function () {
        this.all_purchase_orders = [];
    }
})
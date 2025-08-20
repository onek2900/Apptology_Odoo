/** @odoo-module */

import { PosDB } from "@point_of_sale/app/store/db";
import { patch } from "@web/core/utils/patch";

patch(PosDB.prototype, {
    get_all_sale_orders: function () {
        return this.all_sale_orders;
    },
    remove_all_sale_orders: function () {
        this.all_sale_orders = [];
    }
})
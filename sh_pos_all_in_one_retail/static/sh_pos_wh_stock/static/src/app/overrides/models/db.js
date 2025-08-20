/** @odoo-module */
import { PosDB } from "@point_of_sale/app/store/db";
import { patch } from "@web/core/utils/patch";

patch(PosDB.prototype, {
    get_stock_by_product_id(id){
        return this.quant_by_product_id[id]
    }
})

/** @odoo-module */

import { KitchenOrderlines } from "@sh_pos_kitchen_screen/apps/Components/KitchenOrderlines/KitchenOrderlines";
import { patch } from "@web/core/utils/patch";

patch(KitchenOrderlines.prototype, {
    get_topping_lines(uuids){
        var id_list = eval(uuids)
        var lines = []
        for (let i=0; i< id_list.length; i++){
            const line = this.pos.db.kitchen_order_line_by_uuid[id_list[i]]
            lines.push(line)
        }
        return lines
    }
})
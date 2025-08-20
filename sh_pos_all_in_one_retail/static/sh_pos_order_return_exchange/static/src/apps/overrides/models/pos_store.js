/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { _t } from "@web/core/l10n/translation";


patch(PosStore.prototype, {
    cancel_return_order() {
        var self = this;
        if (this.get_order() && this.get_order().get_orderlines() && this.get_order().get_orderlines().length > 0) {
            [...self.get_order().get_orderlines()].map(async (line) => await self.get_order().removeOrderline(line))
        }
        self.get_order().is_return_order = false;
        self.get_order().is_exchange_order = false;
        self.get_order().old_pos_reference = false;
        self.get_order().old_pos_order_id = false;
        self.showScreen("ProductScreen");
    },
    push_single_order(order) {
        var self = this;
        const result = super.push_single_order(order)
        if (result){
            result.then(function ( Orders ) {
                if ( Orders ){
                    let order_id = Orders[0].id
                    if (self.db.pos_order_by_id[order_id]){
                        if (order.is_return_order || order.is_exchange_order){
                            self.db.pos_order_by_id[order_id][0]['is_return_order'] = order.is_return_order
                            let old_order_id = order.old_pos_order_id
                            let old_order = self.db.pos_order_by_id[old_order_id]
                            if (old_order[0]['old_pos_reference']){
                                old_order[0]['old_pos_reference'] += order.name
                            }else{
                                old_order[0]['old_pos_reference'] = order.name
                            }
                            if (old_order){
                                for(let i=0; i < old_order[1].length; i++){
                                    let new_line = old_order[1][i]
                                    for (let oldline of order.get_orderlines()){
                                        if (oldline.product.id == new_line.product_id){
                                            if( order.is_exchange_order ){
                                                if( oldline.quantity < 0 ){
                                                    // same product wty will not add as return 
                                                    new_line['sh_return_qty'] -= oldline.quantity
                                                }
                                            }else{
                                                new_line['sh_return_qty'] -= oldline.quantity
                                            }
                                            
                                        }
                                    }
                                }
                            }
                        }else{
                            self.orm.call("pos.session", "sh_get_line_data_by_id", [
                                [], Orders[0].lines,
                            ]).then(function (lines) {
                                for(let i=0; i < lines.length; i++){
                                    let new_line = lines[i]
                                    new_line['sh_return_qty'] = 0
                                    self.db.pos_order_line_by_id[new_line.id] = new_line
                                }
                                self.db.pos_order_by_id[order_id][1] = lines
                            })
                        }
                    }
                }
            })
        }
        return result
    }
})
/** @odoo-module */

import { Order } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";


patch(PosStore.prototype, {
    async _processData(loadedData) {
      await super._processData(...arguments);
      this.db.order_by_barcode = {};
      if(loadedData['pos_order_by_id']){
        let orders = Object.values(loadedData['pos_order_by_id'])
        for (var i = 0, len = orders.length; i < len; i++) {
            var each_order = orders[i]; 
            this.db.order_by_barcode[each_order[0].pos_reference.split(' ')[1]] = each_order;
        }
      }
    },
    push_single_order(order) {
      var self = this;
      const result = super.push_single_order(order)
      var date = new Date()
      var date_str =  date.getFullYear() +'-'+  date.getMonth() +'-'+ date.getDate() +'- '+ date.getHours()+':'+ date.getMinutes()+ ':'+ date.getSeconds();
      if (result){
          result.then(async function (Orders) {
              if ( Orders ){ 
                var order_line_list = []
                await self.orm.call("pos.session", "sh_get_line_data_by_id", [
                  [], Orders[0].lines,
                ]).then(function (lines) {
                  for(let i=0; i < lines.length; i++){
                      let new_line = lines[i]
                      new_line['sh_return_qty'] = 0
                      self.db.pos_order_line_by_id[new_line.id] = new_line
                      order_line_list.push(new_line)
                  }
                })
                  let order_id = Orders[0].id
                  let order_data = [{
                      'id': order_id, 
                      'name': Orders[0].name  , 
                      'date_order':  date_str, 
                      'partner_id':  order.get_partner() ? order.get_partner().id : false , 
                      'partner_name':  order.get_partner() ? order.get_partner().name : false , 
                      'pos_reference': order.name, 
                      'amount_total': order.get_total_with_tax() , 
                      'state': Orders[0].account_move ? 'invoiced' : 'paid', 
                  }, order_line_list]
                  self.db.order_by_barcode[order.name.split(' ')[1]] = order_data
              }
          })
      }
      return result
  }
  });
  
patch(Order.prototype, {
    setup(_defaultObj, options) {
        super.setup(...arguments);
        this.from_barcode = false
    },
    set_from_barcode(val){
        this.from_barcode = val
    },

});

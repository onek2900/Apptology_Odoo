/** @odoo-module */

import { Order } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";


patch(PosStore.prototype, {
    async _processData(loadedData) {
      await super._processData(...arguments);
      this.db.order_by_barcode = {};
      try {
        const pobi = loadedData && loadedData['pos_order_by_id'] ? loadedData['pos_order_by_id'] : null;
        if (pobi){
          let orders = Object.values(pobi)
          for (var i = 0, len = orders.length; i < len; i++) {
              var each_order = orders[i];
              if (!each_order || !each_order[0]) continue;
              const pref = String(each_order[0].pos_reference || '');
              const parts = pref.split(' ');
              const key = parts.length > 1 ? parts[1] : pref;
              this.db.order_by_barcode[key] = each_order;
          }
        }
      } catch (_e) { /* ignore */ }
    },
    push_single_order(order) {
      var self = this;
      const result = super.push_single_order(order)
      var date = new Date()
      var date_str =  date.getFullYear() +'-'+  date.getMonth() +'-'+ date.getDate() +'- '+ date.getHours()+':'+ date.getMinutes()+ ':'+ date.getSeconds();
      if (result){
          result.then(async function (Orders) {
              try {
                if (!Array.isArray(Orders) || !Orders.length || !Orders[0]) return;
                var order_line_list = []
                const linesArg = (Orders[0] && Orders[0].lines) ? Orders[0].lines : []
                await self.orm.call("pos.session", "sh_get_line_data_by_id", [
                  [], linesArg,
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
                      'partner_id':  (order && order.get_partner && order.get_partner()) ? order.get_partner().id : false , 
                      'partner_name':  (order && order.get_partner && order.get_partner()) ? order.get_partner().name : false , 
                      'pos_reference': order ? order.name : '', 
                      'amount_total': (order && order.get_total_with_tax) ? order.get_total_with_tax() : 0 , 
                      'state': Orders[0].account_move ? 'invoiced' : 'paid', 
                  }, order_line_list]
                  const pref = String(order ? order.name : '')
                  const parts = pref.split(' ')
                  const key = parts.length > 1 ? parts[1] : pref
                  self.db.order_by_barcode[key] = order_data
              } catch (_e) { /* ignore */ }
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

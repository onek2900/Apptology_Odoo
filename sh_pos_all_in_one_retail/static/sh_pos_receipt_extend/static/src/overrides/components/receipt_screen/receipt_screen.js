/** @odoo-module */

import { ReceiptScreen } from "@point_of_sale/app/screens/receipt_screen/receipt_screen";
import { ReprintReceiptScreen } from "@point_of_sale/app/screens/receipt_screen/reprint_receipt_screen";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";



patch(ReprintReceiptScreen.prototype, {
  setup() {
    super.setup();
    if(this.pos.get_order()){
      this.pos.get_order().is_reciptScreen =  true
    }
    this.receipt_type = "standard";
    this.is_not_standard_size = false;
    var config = this.pos.config;
    if (
      config.sh_enable_a3_receipt ||
      config.sh_enable_a4_receipt ||
      config.sh_enable_a5_receipt
    ) {
      if (config.sh_default_receipt) {
        this.receipt_type = config.sh_default_receipt;
      }
    }
  },

})
patch(ReceiptScreen.prototype, {
  setup() {
    super.setup(...arguments);
    this.receipt_type = "standard";
    this.orm = useService("orm");
    this.is_not_standard_size = false;
    var config = this.pos.config;
    if (
      config.sh_enable_a3_receipt ||
      config.sh_enable_a4_receipt ||
      config.sh_enable_a5_receipt
    ) {
      if (config.sh_default_receipt) {
        this.receipt_type = config.sh_default_receipt;
      }
    }
    this.amount_in_words();
    this.get_order_details();
  },

  async get_order_details() {
    let order = this.pos.get_order();
    let Orders = await this.orm.call("pos.order", "search_read", [
      [["pos_reference", "=", order.name]],
    ]);
    // if (order.is_to_invoice() && this.pos.config.sh_pos_receipt_invoice) {
      if (Orders) {
        if(Orders.length > 0){
          if(Orders[0]['name']){
            order["order_name"] = Orders[0]['name'];
          }
          if(Orders[0]["account_move"] && Orders[0]["account_move"][1]){
            var invoice_number = Orders[0]["account_move"][1].split(" ")[0];
            order["invoice_number"] = invoice_number;
          }
        }
        // if (
        //   Orders.length > 0 &&
        //   Orders[0]["account_move"] &&
        //   Orders[0]["account_move"][1]
        // ) {
        //   var invoice_number = Orders[0]["account_move"][1].split(" ")[0];
        //   order["invoice_number"] = invoice_number;
        // }
        this.render();
      }
    // }
  },

  async amount_in_words() {
    var total_with_tax_in_words = "";
    var self = this;
    let cur = await self.orm.call("res.currency", "amount_to_text", [
      self.pos.currency.id,
      self.pos.get_order().get_total_with_tax(),
    ]);
    if (cur) {
      total_with_tax_in_words = cur;
    }

    self.pos.get_order().total_with_tax_in_words = total_with_tax_in_words;
  },

  async printA3Receipt() {
    this.receipt_type = "a3_size";
    await this.render();
    this.is_not_standard_size = true;
    this.printReceipt();
  },
  async printA4Receipt() {
    this.receipt_type = "a4_size";
    await this.render();
    this.is_not_standard_size = true;
    this.printReceipt();
  },

  async printA5Receipt() {
    this.receipt_type = "a5_size";
    await this.render();
    this.is_not_standard_size = true;
    this.printReceipt();
  },

  async printReceipt() {
    if (this.is_not_standard_size == false) {
      this.receipt_type = "standard";
      await this.render();
    }

    await super.printReceipt();
    this.is_not_standard_size = false;
  },
});

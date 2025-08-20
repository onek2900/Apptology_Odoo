/** @odoo-module */

import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";
import { usePos } from "@point_of_sale/app/store/pos_hook";
patch(PaymentScreen.prototype, {
    setup() {
        super.setup();
        this.pos = usePos();
    },
    async validateOrder(isForceValidate) {
        var self = this;
        this.pos.cash_in_out_receipt = false;
        this.pos.cash_in_out_statement_receipt = false;
        super.validateOrder(isForceValidate);
        var order = self.pos.get_order().export_as_JSON();
        var date_obj = new Date(self.pos.get_order().date_order);
        var date = date_obj.getFullYear() + "-" + ("0" + (date_obj.getMonth() + 1)).slice(-2) + "-" + ("0" + date_obj.getDate()).slice(-2);
        var order_data = {};
        if (order.statement_ids && order.statement_ids.length > 0) {
            for(let each_statement of order.statement_ids){
                if (each_statement[2]) {
                    order_data = {
                        pos_order_id: [order.uid, order.name],
                        payment_method_id: [each_statement[2]["payment_method_id"], self.pos.payment_methods_by_id[each_statement[2]["payment_method_id"]].name],
                        amount: each_statement[2]["amount"],
                        payment_date: date,
                    };
                    self.pos.db.all_payment.push(order_data);
                    self.pos.db.payment_line_by_ref[order_data.pos_order_id] = order_data;
    
                    if (self.pos.payment_methods_by_id[each_statement[2]["payment_method_id"]].is_cash_count) {
                        self.pos.pos_session.cash_register_total_entry_encoding = self.pos.pos_session.cash_register_total_entry_encoding + parseFloat(each_statement[2]["amount"] - order.amount_return);
                        self.pos.pos_session.cash_register_balance_end = self.pos.pos_session.cash_register_balance_end + parseFloat(each_statement[2]["amount"] - order.amount_return);
                    }
                }
            };
        }
        if (order.amount_return) {
            order_data = { pos_order_id: [order.uid, order.name], payment_method_id: [1, "Cash"], amount: -order.amount_return, payment_date: date };
            self.pos.db.all_payment.push(order_data);
            self.pos.db.payment_line_by_ref[order_data.pos_order_id] = order_data;
        }
    }
});
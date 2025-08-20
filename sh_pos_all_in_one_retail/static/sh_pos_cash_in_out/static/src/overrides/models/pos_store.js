/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";

    patch(PosStore.prototype, {
        async setup(env, { popup, orm, number_buffer, hardware_proxy, barcode_reader, ui }) {
            await super.setup(...arguments);
             this.db.all_order = [];
             this.db.all_payment_method = [];
             this.db.all_cash_in_out_statement = [];
             this.db.all_cash_in_out_statement_id = [];
             this.db.display_cash_in_out_statement = [];
             this.db.payment_method_by_id = {};
             this.db.all_payment = [];
             this.db.payment_line_by_id = {};
             this.db.payment_line_by_ref = {};
             this.db.all_cash_in_out = [];
        },
        async _processData(loadedData) {
            await super._processData(...arguments);
            if(loadedData['sh.cash.in.out']){
                this.db.all_cash_in_out_statement = loadedData['sh.cash.in.out']
            }
            this.db.all_payment_method = loadedData['pos.payment.method'] || [];
            this.db.payment_method_by_id =  loadedData['payment_method_by_id'] || [];
            this.db.all_payment =  loadedData['pos.payment'] || [];
            this.cash_register_total_entry_encoding = loadedData['pos.session'].cash_register_total_entry_encoding || 0;
            this.cash_register_balance_end = loadedData['pos.session'].cash_register_balance_end || 0;
            this.cash_register_balance_end_real = loadedData['pos.session'].cash_register_balance_end_real || 0;
            this.cash_register_balance_start = loadedData['pos.session'].cash_register_balance_start || 0;
            this.display_cash_in_out_statement = [];
        },
        get_cashier_user_id() {
            return this.user.id || false;
        }
    })

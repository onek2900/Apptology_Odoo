/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";


export class CashInOutOptionStatementPopupWidget extends AbstractAwaitablePopup {
    static template = "sh_pos_cash_in_out.CashInOutOptionStatementPopupWidget";
        setup() {
            super.setup();
            this.orm = useService("orm");
            this.pos = usePos();
            this.report = useService("report");
            this.showStatementDate = useState({
                changeStatementOption : ''
            })
            this.statement_vals = useState({
                statementValue : false,
                statementPrintValue : false
            })
        }
        async print() {
            var self = this;
            var statementValue = $("input[name='statement_option']:checked").val();
            var statementPrintValue = $("input[name='print_option']:checked").val();
            if (statementValue && statementPrintValue) {
                let all_cash_in_out_statement =  await this.orm.call("sh.cash.in.out", "search_read", [
                    [['sh_session', '=', self.pos.pos_session.id]]
                ])
                if (statementValue == "current_session" && statementPrintValue == "pdf") {
                    if(all_cash_in_out_statement) {
                        self.pos.db.all_cash_in_out_statement_id = [];
                        if (all_cash_in_out_statement && all_cash_in_out_statement.length > 0) {
                            for(let each_cash_in_out_statement of all_cash_in_out_statement){   
                                if (
                                    self.pos.pos_session &&
                                    self.pos.pos_session.id &&
                                    each_cash_in_out_statement.sh_session &&
                                    each_cash_in_out_statement.sh_session[0] &&
                                    each_cash_in_out_statement.sh_session[0] == self.pos.pos_session.id
                                ) {
                                    self.pos.db.all_cash_in_out_statement_id.push(each_cash_in_out_statement.id);
                                }
                            };
                        }
                        if (self.pos.db.all_cash_in_out_statement_id && self.pos.db.all_cash_in_out_statement_id.length > 0) {
                            self.report.doAction("sh_pos_all_in_one_retail.sh_pos_cash_in_out_report", [self.pos.db.all_cash_in_out_statement_id
                            ]
                            );
                        } else {
                            alert("No Any Cash In / Cash Out Statement for this Session.");
                        }
                    };
                    this.props.close({ confirmed: true, payload: await this.getPayload() });
                } else if (statementValue == "current_session" && statementPrintValue == "receipt") {
                    if (all_cash_in_out_statement && all_cash_in_out_statement.length) {
                        self.pos.display_cash_in_out_statement = [];
                        
                        for(let each_cash_in_out_statement of all_cash_in_out_statement){
                            if (
                                self.pos.pos_session &&
                                self.pos.pos_session.id &&
                                each_cash_in_out_statement.sh_session &&
                                each_cash_in_out_statement.sh_session[0] &&
                                each_cash_in_out_statement.sh_session[0] == self.pos.pos_session.id
                                ) {
                                self.pos.display_cash_in_out_statement.push(each_cash_in_out_statement);
                            } else if (
                                self.pos.pos_session &&
                                self.pos.pos_session.id &&
                                each_cash_in_out_statement.sh_session &&
                                each_cash_in_out_statement.sh_session &&
                                each_cash_in_out_statement.sh_session == self.pos.pos_session.id
                                ) {
                                    self.pos.display_cash_in_out_statement.push(each_cash_in_out_statement);
                            }
                        };
                        if (self.pos.display_cash_in_out_statement && self.pos.display_cash_in_out_statement.length > 0) {
                            self.pos.cash_in_out_statement_receipt = true;
                            self.pos.showScreen("ReceiptScreen");
                        } else {
                            alert("No Any Cash In / Cash Out Statement avilable for this session.");
                        }
                    } else {
                        alert("No Any Cash In / Cash Out Statement avilable.");
                    }
                    this.props.close({ confirmed: true, payload: await this.getPayload() });
                } else if (statementValue == "date_wise" && statementPrintValue == "pdf") {
                    if ($(".start_date").val() && $(".end_date").val()) {
                        if ($(".start_date").val() > $(".end_date").val()) {
                            alert("Start Date must be less than End Date.");
                        } else {
                            var start_date = $(".start_date").val() + " 00:00:00";
                            var end_date = $(".end_date").val() + " 24:00:00";
                            let all_cash_in_out_statement =await this.orm.call("sh.cash.in.out", "search_read", [
                                [['sh_date','>=',start_date],["sh_date", "<=", end_date]]
                            ])
                           if(all_cash_in_out_statement) {
                                self.pos.db.all_cash_in_out_statement_id = [];
                                if (all_cash_in_out_statement && all_cash_in_out_statement.length > 0) {
                                    for(let each_cash_in_out_statement of all_cash_in_out_statement){
                                        self.pos.db.all_cash_in_out_statement_id.push(each_cash_in_out_statement.id);
                                    };

                                    if (self.pos.db.all_cash_in_out_statement_id && self.pos.db.all_cash_in_out_statement_id.length > 0) {
                                        self.report.doAction("sh_pos_all_in_one_retail.sh_pos_cash_in_out_date_wise_report", [ self.pos.db.all_cash_in_out_statement_id
                                            ]
                                        );
                                    }
                                    this.props.close({ confirmed: true, payload: await this.getPayload() });
                                } else {
                                    alert("No Cash In / Out Statement Between Given Date.");
                                }
                            };
                        }
                    } else {
                        alert("Enter Start Date or End Date.");
                    }
                } else if (statementValue == "date_wise" && statementPrintValue == "receipt") {
                    if ($(".start_date").val() && $(".end_date").val()) {
                        if ($(".start_date").val() > $(".end_date").val()) {
                            alert("Start Date must be less than End Date.");
                        } else {
                            var start_date = $(".start_date").val() + " 00:00:00";
                            var end_date = $(".end_date").val() + " 24:00:00";
                            let all_cash_in_out_statement =await this.orm.call("sh.cash.in.out", "search_read", [
                                [['sh_date','>=',start_date],["sh_date", "<=", end_date]]
                            ])
                            if (all_cash_in_out_statement && all_cash_in_out_statement.length > 0) {
                                self.pos.display_cash_in_out_statement = [];
                                for(let each_cash_in_out_statement of all_cash_in_out_statement){
                                    if (each_cash_in_out_statement.sh_date && each_cash_in_out_statement.sh_date >= start_date && each_cash_in_out_statement.sh_date <= end_date) {
                                        self.pos.display_cash_in_out_statement.push(each_cash_in_out_statement);
                                    }
                                };
                                if (self.pos.display_cash_in_out_statement && self.pos.display_cash_in_out_statement.length > 0) {
                                    self.pos.cash_in_out_statement_receipt = true;
                                    self.pos.showScreen("ReceiptScreen");
                                } else {
                                    alert("No Cash In / Out Statement Between Given Date.");
                                }
                                this.props.close({ confirmed: true, payload: await this.getPayload() });
                            } else {
                                alert("No Any Cash In / Cash Out Statement avilable.");
                            }
                        }
                    } else {
                        alert("Enter Start Date or End Date.");
                    }
                }
            }     
            this.cancel()       
        }
        changeStatementOption(event){
            if ($(event.target).val() == "current_session") {
                $(".sh_statement_date").removeClass("show");
            } else if ($(event.target).val() == "date_wise") {
                $(".sh_statement_date").addClass("show");
            }
        }
    }
  
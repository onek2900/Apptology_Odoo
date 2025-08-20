/** @odoo-module */
import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
import { usePos } from "@point_of_sale/app/store/pos_hook";
// import { ReceiptScreen } from "@point_of_sale/../tests/tours/helpers/ReceiptScreenTourMethods";
import { useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { formatFloat, formatMonetary } from "@web/views/fields/formatters";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";

export class ZReportOptionPopup extends AbstractAwaitablePopup {
    static template = "sh_pos_z_report.ZReportOptionPopup";
    setup() {
        super.setup();
        this.pos = usePos();
        this.report = useService("report");
    }
    async print() {
        var self = this;
        var statementPrintValue = $("input[name='print_option']:checked").val();

        if (statementPrintValue) {
            if (statementPrintValue == "pdf") {
                this.report.doAction("sh_pos_all_in_one_retail.pos_z_report_detail", [
                    this.pos.pos_session.id,
                ]);
            } else if (statementPrintValue == "receipt" && self.pos.pos_session && self.pos.pos_session.id) {
                const session_detail = await self.pos.orm.silent.call("pos.session", "get_session_detail", [
                    self.pos.pos_session.id
                ]);
                if(session_detail){
                    self.pos.is_z_report_receipt = true
                    self.pos.session_data = session_detail
                    self.pos.showScreen("ReceiptScreen");
                }
            }
        }     
        this.cancel()       
    }
}
  
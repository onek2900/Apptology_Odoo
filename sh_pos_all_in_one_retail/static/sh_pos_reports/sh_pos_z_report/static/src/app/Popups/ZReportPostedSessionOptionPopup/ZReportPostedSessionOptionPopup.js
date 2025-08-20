/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";

export class ZReportPostedSessionOptionPopup extends AbstractAwaitablePopup {
    static template = "sh_pos_z_report.ZReportPostedSessionOptionPopup";
    setup() {
        super.setup();
        this.pos = usePos();
        this.report = useService("report");
    }
    async print(){
        var self = this;
        var sessionSelection = parseInt($(".sh_session_selection").val());
        if(self.pos.config.sh_allow_z_report_type == 'both'){
            var statementPrintValue = $("input[name='print_option']:checked").val();
            if(sessionSelection && statementPrintValue){
                if (statementPrintValue == "pdf") {
                    this.report.doAction("sh_pos_all_in_one_retail.pos_z_report_detail", [
                        sessionSelection,
                    ]);
                } else if (statementPrintValue == "receipt") {
                    const session_detail = await self.pos.orm.silent.call("pos.session", "get_session_detail", [
                        sessionSelection
                    ]);
                    if(session_detail){
                        self.pos.is_z_report_receipt = true
                        self.pos.session_data = session_detail
                        self.pos.showScreen("ReceiptScreen");
                    }
                }
            }
        }else if(self.pos.config.sh_allow_z_report_type == 'pdf'){
            this.report.doAction("sh_pos_all_in_one_retail.pos_z_report_detail", [
                sessionSelection,
            ]);
        }else if(self.pos.config.sh_allow_z_report_type == 'receipt'){
            const session_detail = await self.pos.orm.silent.call("pos.session", "get_session_detail", [
                sessionSelection
            ]);
            if(session_detail){
                self.pos.is_z_report_receipt = true
                self.pos.session_data = session_detail
                self.pos.showScreen("ReceiptScreen");
            }
        }
        this.cancel()
    }
}

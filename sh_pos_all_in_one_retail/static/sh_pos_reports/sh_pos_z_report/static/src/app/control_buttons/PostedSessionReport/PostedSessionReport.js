  /** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { ZReportPostedSessionOptionPopup } from "@sh_pos_all_in_one_retail/static/sh_pos_reports/sh_pos_z_report/app/Popups/ZReportPostedSessionOptionPopup/ZReportPostedSessionOptionPopup";

export class PostedSessionReport extends Component {
    static template = "sh_pos_z_report.PostedSessionReport";
    setup() {
        super.setup();
        this.pos = usePos();
        this.popup = useService("popup");
    }
    async onClick(){
        var self = this;
        if(self && self.pos && self.pos.db && self.pos.db.posted_session_ids && self.pos.db.posted_session_ids.length > 0){
            let { confirmed } = await this.popup.add(ZReportPostedSessionOptionPopup);
            if (confirmed) {
            } else {
                return;
            }
        }else{
            alert("No Any Posted Session Found.")
        }
    }
}

ProductScreen.addControlButton({
    component: PostedSessionReport,
    condition: function () {
        if(!this.pos.config.module_pos_hr){
            return this.pos.config.sh_enable_z_report && this.pos.user.sh_is_allow_z_report && this.pos.config.sh_allow_posted_session_report;
        }else{
            if(this.pos.get_cashier() && this.pos.get_cashier().name){
                return this.pos.get_cashier().sh_is_allow_z_report && this.pos.config.sh_enable_z_report && this.pos.config.sh_allow_posted_session_report
            }else{
                return false
            }
            
        }
    },
})

  /** @odoo-module **/

  import { _t } from "@web/core/l10n/translation";
  import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
  import { useService } from "@web/core/utils/hooks";
  import { Component } from "@odoo/owl";
  import { usePos } from "@point_of_sale/app/store/pos_hook";
  import { ZReportOptionPopup } from "@sh_pos_all_in_one_retail/static/sh_pos_reports/sh_pos_z_report/app/Popups/ZReportOptionPopup/ZReportOptionPopup";
  
  export class ShPosZReport extends Component {
      static template = "sh_pos_z_report.ShPosZReport";
      setup() {
        super.setup();
        this.report = useService("report");
        this.pos = usePos();
        this.popup = useService("popup");
    }
    async onClick(){
        var self = this;
        if(self && self.pos && self.pos.config && self.pos.config.sh_allow_z_report_type && self.pos.config.sh_allow_z_report_type == 'pdf'){
            this.report.doAction("sh_pos_all_in_one_retail.pos_z_report_detail", [
                this.pos.pos_session.id,
            ]);
        }else if(self && self.pos && self.pos.config && self.pos.config.sh_allow_z_report_type && self.pos.config.sh_allow_z_report_type == 'receipt' && self.pos.pos_session && self.pos.pos_session.id){
            let domain = [];
            const session_detail = await self.pos.orm.silent.call("pos.session", "get_session_detail", [
                self.pos.pos_session.id
            ]);
            if(session_detail){
                self.pos.is_z_report_receipt = true
                self.pos.session_data = session_detail
                self.pos.showScreen("ReceiptScreen");
            }
        }else if(self && self.pos && self.pos.config && self.pos.config.sh_allow_z_report_type && self.pos.config.sh_allow_z_report_type == 'both' && self.pos.pos_session && self.pos.pos_session.id){
            let { confirmed } = await this.popup.add(ZReportOptionPopup);
                if (confirmed) {
                } else {
                    return;
                }
        }
    }
   
  }

  ProductScreen.addControlButton({
    component: ShPosZReport,
    condition: function () {
        if(!this.pos.config.module_pos_hr){
            return this.pos.config.sh_enable_z_report && this.pos.user.sh_is_allow_z_report;
        }else{
            if(this.pos.get_cashier() && this.pos.get_cashier().name){
                return this.pos.get_cashier().sh_is_allow_z_report && this.pos.config.sh_enable_z_report
            }else{
                return false
            }
            
        }
    },
});

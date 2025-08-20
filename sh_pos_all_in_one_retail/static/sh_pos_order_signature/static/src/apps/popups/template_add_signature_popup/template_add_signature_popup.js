/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { onMounted } from "@odoo/owl";

// formerly ConfirmPopupWidget
export class TemplateAddSignaturePopupWidget extends AbstractAwaitablePopup {
    static template = "sh_pos_all_in_one_retail.TemplateAddSignaturePopupWidget";
    setup(){
        super.setup()
        this.pos = usePos();
        onMounted(() => {
            console.log("$(#signature) >>> ",$("#signature"))
            $("#signature").jSignature();

            if (this.pos.config.sh_enable_date) {
                var today = new Date();
                var dd = String(today.getDate()).padStart(2, "0");
                var mm = String(today.getMonth() + 1).padStart(2, "0");
                var yyyy = today.getFullYear();
                today = yyyy + "-" + mm + "-" + dd;
                $("#sh_date").val(today);
            }
        })
    }
    clear() {
        $("#signature").jSignature("reset");
    }
    async confirm() {
        var self = this;
        this.props.resolve({ confirmed: true, payload: await this.getPayload() });
        if ($("#signature").jSignature("getData", "native").length > 0) {
            var value = $("#signature").jSignature("getData", "image");
            self.pos.get_order().set_signature(value[1]);
        }
        if (self.pos.config.sh_enable_name) {
            var name = $("#sh_name").val();
            if (name) {
                self.pos.get_order().set_signature_name(name);
            }
        }
        if (self.pos.config.sh_enable_date) {
            var date = $("#sh_date").val();
            if (date) {
                self.pos.get_order().set_signature_date(date);
            }
        }
        super.confirm()
    }
}

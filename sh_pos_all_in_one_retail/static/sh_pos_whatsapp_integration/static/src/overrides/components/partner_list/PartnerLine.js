/** @odoo-module */
import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { PartnerLine } from "@point_of_sale/app/screens/partner_list/partner_line/partner_line";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { WhatsappMessagePopup } from "@sh_pos_all_in_one_retail/static/sh_pos_whatsapp_integration/apps/popups/WhatsappMessagePopup/WhatsappMessagePopup";

patch(PartnerLine.prototype, {
    setup(){
        super.setup();
        this.popup = useService("popup");
    },
    async on_click_send_wp(event) {
        var message = "";
        var self = this;
        if (this.env.services.pos.user.sign) {
            message += "%0A%0A%0A" + this.env.services.pos.user.sign;
        }
        console.log("event >>> ",event)
        const partner = this.props.partner;
        if(partner.mobile){
            
            const { confirmed } = await this.popup.add(WhatsappMessagePopup, {
                title: 'Carry Bag List',
                mobile_no: partner.mobile,
                message: message.replace('&','%26'),
                confirmText: "Send",
                cancelText: "Cancel",
            });
            if (confirmed) {
                var text_msg = $('textarea[name="message"]').val();
                var mobile = $(".mobile_no").val();
                if (text_msg && mobile) {
                    var href = "https://web.whatsapp.com/send?l=&phone=" + mobile + "&text=" + text_msg.replace('&','%26');
                    $(".wp_url").attr("href", href);
                    $(".wp_url span").trigger("click");
                } else {
                    this.popup.add(ErrorPopup, {
                        title: _t('  '),
                        body: _t('Please Enter Message'),
                    });
                }
            }
        }

        else{
            this.popup.add(ErrorPopup, {
                title: _t(' Mobile Number Not Found '),
                body: _t('Please Enter mobile number for this partner'),
            });
        }
       
    }
})

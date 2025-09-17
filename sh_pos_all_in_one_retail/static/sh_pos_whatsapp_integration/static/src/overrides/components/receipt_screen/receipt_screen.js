/** @odoo-module */

import { ReceiptScreen } from "@point_of_sale/app/screens/receipt_screen/receipt_screen";
import { patch } from "@web/core/utils/patch";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { WhatsappMessagePopup } from "@sh_pos_all_in_one_retail/static/sh_pos_whatsapp_integration/apps/popups/WhatsappMessagePopup/WhatsappMessagePopup";

patch(ReceiptScreen.prototype, {
    setup() {
      super.setup()
      this.popup = useService("popup");
    },
    async on_click_send_wp_direct(event) {
      var message = "";
      var self = this;

      const partner = this.currentOrder.get_partner();
      if (partner.mobile) {
          var mobile = partner.mobile;
          var order = this.currentOrder;
          var receipt = this.currentOrder.export_for_printing();
          var orderlines = this.currentOrder.get_orderlines();
          var paymentlines = this.currentOrder.get_paymentlines();
          message +=
              "Dear " +
              partner.name +
              "," +
              "%0A%0A" +
              "Here is the order " +
              "*" +
              receipt.name +
              "*" +
              " amounting in " +
              "*" +
              self.env.utils.formatCurrency(parseFloat(receipt.amount_total.toFixed(2))) +
              "*" +
              " from " +
              receipt.headerData.company.name +
              "%0A%0A";
          if (receipt.orderlines.length > 0) {
              message += "Following is your order details." + "%0A";
              for (const orderline of receipt.orderlines) {
                    message += "%0A" + "*" + orderline.productName + "*" + "%0A" + "*Qty:* " + orderline.qty + "%0A" + "*Price:* " + orderline.price +  "%0A";
                    if (orderline.discount > 0) {
                        message += "*Discount:* " + orderline.discount + "%25" + "%0A";
                    }
              };
              message += "________________________" + "%0A";
          }
          message += "*" + "Total Amount:" + "*" + "%20" + self.env.utils.formatCurrency(parseFloat(receipt.amount_total.toFixed(2)));
          if (this.pos.user.sign) {
              message += "%0A%0A%0A" + this.pos.user.sign;
          }
          $(".default-view").append('<a class="wp_url" target="blank" href=""><span></span></a>');
          var href = "https://web.whatsapp.com/send?l=&phone=" + mobile + "&text=" + message.replace('&','%26');
          $(".wp_url").attr("href", href);
          $(".wp_url span").trigger("click");
      }
      else{
        this.popup.add(ErrorPopup, {
            title: _t(' Mobile Number Not Found '),
            body: _t('Please Enter mobile number for this partner'),
        });
      }
    },
    async on_click_send_wp(event) {
        var message = "";
        var self = this;
        const partner = this.currentOrder.get_partner();
        if (partner && partner.mobile) {
            var mobile = partner.mobile;
            var receipt = this.currentOrder.export_for_printing();
        
            message +=
                "Dear " +
                partner.name +
                "," +
                "%0A%0A" +
                "Here is the order " +
                "*" +
                receipt.name +
                "*" +
                " amounting in " +
                "*" +
                self.env.utils.formatCurrency(parseFloat(receipt.amount_total.toFixed(2))) +
                "*" +
                " from " +
                receipt.headerData.company.name +
                "%0A%0A";
            if (receipt.orderlines.length > 0) {
                message += "Following is your order details." + "%0A";
                for (const orderline of receipt.orderlines) {
                    message += "%0A" + "*" + orderline.productName + "*" + "%0A" + "*Qty:* " + orderline.qty + "%0A" + "*Price:* " + orderline.price +  "%0A";
                    if (orderline.discount > 0) {
                        message += "*Discount:* " + orderline.discount + "%25" + "%0A";
                    }
                };
                message += "________________________" + "%0A";
            }
            message += "*" + "Total Amount:" + "*" + "%20" + self.env.utils.formatCurrency(parseFloat(receipt.amount_total.toFixed(2)));
            if (this.pos.user.sign) {
                message += "%0A%0A%0A" + this.pos.user.sign;
            }
            // const { confirmed } = await this.popup.add("WhatsappMessagePopup", {
            //     mobile_no: partner.mobile,
            //     message: message.replace('&','%26'),
            //     confirmText: "Send",
            //     cancelText: "Cancel",
            // });
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
                    Gui.showPopup("ErrorPopup", {
                        'title': "",
                        'body': "Please Enter Message",
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

});

/** @odoo-module **/
import { ReceiptScreen } from "@point_of_sale/app/screens/receipt_screen/receipt_screen";
import { OrderReceipt } from "@point_of_sale/app/screens/receipt_screen/receipt/order_receipt";
import { patch } from "@web/core/utils/patch";
import { useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";


patch(ReceiptScreen.prototype, {
    setup(){
        super.setup();
        this.buttonDownloadReceipt = useRef("order-download-receipt-button");
        this.rpc = useService("rpc");
        this.notification = useService("notification");

    },

    async downloadReceipt(){

        this.buttonDownloadReceipt.el.className = "fa fa-fw fa-spin fa-circle-o-notch";

        const el = await this.renderer.toHtml(OrderReceipt, {data: this.pos.get_order().export_for_printing(), formatCurrency: this.env.utils.formatCurrency});
        const order = this.pos.get_order()

        const renderedCanvas = await html2canvas(el, {
            useCORS: true,
        });
        const imageURL = renderedCanvas.toDataURL('image/png');
        const base64Data = imageURL.split(',')[1]

        await this.rpc("/save/order_receipt_image", {
            tracking_number: order.trackingNumber,
            image_data: base64Data,
            name: order.name,
        }).then(res => {
            if (res.status === 'success') {
                this.notification.add(_t(res.message), { type: "success" });
            }
        })

        if (this.buttonDownloadReceipt.el) {
            this.buttonDownloadReceipt.el.className = "fa fa-file-image-o ms-2";
        }
    },

})
/** @odoo-module **/
import { ReceiptScreen } from "@point_of_sale/app/screens/receipt_screen/receipt_screen";
import { patch } from "@web/core/utils/patch";
import { PrinterReceipt } from "../printer_receipt/printer_receipt"
import { useRef } from "@odoo/owl";



patch(ReceiptScreen.prototype, {
    setup(){
        super.setup();
        this.buttonOrderPrinting = useRef("orderPrintingBtn");
    },

    async handleOrderPrinting(event) {
        this.buttonOrderPrinting.el.className = "fa fa-fw fa-spin fa-circle-o-notch";
        const order = this.pos.get_order();
        console.log( "orderPrinting");
        const lines = order.orderlines.map((orderline) => ({
            name:orderline.full_product_name,
            note: orderline.note,
            product_id: orderline.product.id,
            quantity: orderline.quantity,
            category_ids: this.pos.db.get_category_by_id(orderline.product.pos_categ_ids),
            customerNote: orderline.customerNote,
        }))

        for (const printer of this.pos.unwatched.printers) {
            const data = this._getPrintingCategoriesChanges(
                printer.config.product_categories_ids,
                lines,
            );
            if (data.length > 0) {
                // $(document.querySelector(".render-container")).empty();
                // //
                // const el = await this.renderer.toHtml(PrinterReceipt, {
                //     data,
                //     headerData: order.export_for_printing().headerData,
                //     printer
                // });
                // this.renderer.whenMounted({ el, callback: window.print });

                // Get the printer name
                // const printerName = el.querySelector('.printer-name h6').textContent;
                const printerName = printer.config.name;
                // Get the cashier name
                // const cashierName = el.querySelector('.cashier div').textContent;
                const cashierName = order.export_for_printing().headerData.cashier;
                // Get the order number
                // const orderNumber = el.querySelector('.pos-receipt-contact .fw-bolder .fs-2').textContent;
                const orderNumber = order.export_for_printing().headerData.trackingNumber;
                // Get all line items
                // const lineItems = el.querySelectorAll('.line-item');
                // Log the extracted information
                console.log(`Order Start:`);

                console.log(`Printer: ${printerName}`);
                console.log(`Cashier: ${cashierName}`);
                console.log(`Order Number: ${orderNumber}`);
                console.log(`Category\t\tOrder\t\tQuantity`);
                // Loop through each line item and extract product details
                // lineItems.forEach((item) => {
                //     const category = item.querySelector('.line-item__category span').textContent;
                //     const productName = item.querySelector('.line-item__product').textContent;
                //     const productQty = item.querySelector('.line-item__qty').textContent;
                //     console.log(`OrderlinesQTY:${productName}:${productQty}`);
                // });
                data.forEach(item => {
                    const category = item.category_ids.map(cat => cat.name).join(",");
                    const productName = item.name;
                    const productQty = item.quantity;
                    const customerNote = item.customerNote;
                    console.log(`OrderlinesQTY:${productName}:${productQty}`);
                    console.log(`customerNote:${customerNote}`);

                })
                console.log(`Order Completed`);

            }
        }

        if (this.buttonOrderPrinting.el) {
            this.buttonOrderPrinting.el.className = "fa fa-file-image-o ms-2";
        }
    },
    _getPrintingCategoriesChanges(categories, currentOrderChange) {
        return currentOrderChange.filter((line) =>
            this.pos.db.is_product_in_category(categories, line["product_id"])
        )
    }
})
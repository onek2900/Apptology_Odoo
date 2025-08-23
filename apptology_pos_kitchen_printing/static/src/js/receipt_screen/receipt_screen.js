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

                const printerName = printer.config.name;

                const cashierName = order.export_for_printing().headerData.cashier;

                const orderNumber = order.export_for_printing().headerData.trackingNumber;

                console.log(`Order Start:`);

                console.log(`Printer: ${printerName}`);
                console.log(`Cashier: ${cashierName}`);
                console.log(`Order Number: ${orderNumber}`);
                console.log(`Category\t\tOrder\t\tQuantity`);

                data.forEach(item => {
                    const category = item.category_ids.map(cat => cat.name).join(",");
                    const productName = item.name;
                    const productQty = item.quantity;
                    const customerNote = item.customerNote;
                    console.log(`OrderlinesQTY:${productName}:${productQty}:${customerNote}`);

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
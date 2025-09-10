/** @odoo-module **/
import { ReceiptScreen } from "@point_of_sale/app/screens/receipt_screen/receipt_screen";
import { patch } from "@web/core/utils/patch";
import { PrinterReceipt } from "../printer_receipt/printer_receipt"
// Debug helper gated by localStorage flag
function dbg(...args) {
    try {
        if (window?.localStorage?.getItem('POS_DEBUG_KITCHEN') === '1') {
            // eslint-disable-next-line no-console
            console.log(...args);
        }
    } catch (_) {}
}
import { useRef } from "@odoo/owl";



patch(ReceiptScreen.prototype, {
    setup(){
        super.setup();
        this.buttonOrderPrinting = useRef("orderPrintingBtn");
    },

    async handleOrderPrinting(event) {
        this.buttonOrderPrinting.el.className = "fa fa-fw fa-spin fa-circle-o-notch";
        const order = this.pos.get_order();
        dbg("orderPrinting");
        const lines = order.orderlines.map((orderline) => ({
            name: orderline.full_product_name,
            note: orderline.note,
            product_id: orderline.product.id,
            quantity: orderline.quantity,
            category_ids: this.pos.db.get_category_by_id(orderline.product.pos_categ_ids),
            customerNote: orderline.customerNote,
            // flags and parent linkage (when available from toppings module)
            is_topping: !!(orderline.is_topping || orderline.sh_is_topping),
            is_has_topping: !!(orderline.is_has_topping || orderline.sh_is_has_topping),
            parent_line_id: orderline.sh_topping_parent ? orderline.sh_topping_parent.id : null,
            parent_name: orderline.sh_topping_parent ? orderline.sh_topping_parent.full_product_name : null,
            toppings_count: Array.isArray(orderline.Toppings) ? orderline.Toppings.length : (orderline.Toppings ? 1 : 0),
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

                // Build a single structured JSON log per printer
                const jsonLog = {
                    type: "kitchen_printer_log",
                    printer: printerName,
                    cashier: cashierName,
                    order_number: orderNumber,
                    lines: data.map((item) => ({
                        categories: item.category_ids.map((cat) => cat.name),
                        name: item.name,
                        qty: item.quantity,
                        note: item.customerNote,
                        is_topping: !!item.is_topping,
                        has_topping: !!item.is_has_topping,
                        parent_line_id: item.parent_line_id || null,
                        parent_name: item.parent_name || null,
                        toppings_count: item.toppings_count || 0,
                    })),
                };
                try {
                    dbg(JSON.stringify(jsonLog));
                } catch (e) {
                    // keep a single warning for actual stringify failures
                    // eslint-disable-next-line no-console
                    console.warn("Failed to stringify kitchen printer log", e);
                }
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

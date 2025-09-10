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
        // eslint-disable-next-line no-console
        console.log("orderPrinting");
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
                    // eslint-disable-next-line no-console
                    console.log(JSON.stringify(jsonLog));
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
        function normalizeCategoryIds(cats) {
            if (!cats) return [];
            if (cats instanceof Set) return Array.from(cats);
            if (!Array.isArray(cats)) return [];
            return cats
                .map((c) => {
                    if (typeof c === "number") return c;
                    if (Array.isArray(c)) return c[0];
                    if (c && typeof c === "object") return c.id ?? c.ID ?? c["_id"] ?? null;
                    return null;
                })
                .filter((x) => typeof x === "number" && !Number.isNaN(x));
        }
        const printerCatIds = normalizeCategoryIds(categories);
        if (!printerCatIds.length) return [];
        const printerCatSet = new Set(printerCatIds);
        function isMatchWithAncestors(catIds) {
            for (const cid of catIds) {
                let cur = cid;
                while (cur) {
                    if (printerCatSet.has(cur)) return true;
                    const node = this.pos?.db?.category_by_id?.[cur];
                    cur = node?.parent_id || null;
                }
            }
            return false;
        }
        return currentOrderChange.filter((line) => {
            const lineCatIds = normalizeCategoryIds(line.category_ids);
            if (lineCatIds.length) return isMatchWithAncestors.call(this, lineCatIds);
            const product = this.pos?.db?.product_by_id?.[line.product_id];
            const prodCats = normalizeCategoryIds(product?.pos_categ_ids);
            return isMatchWithAncestors.call(this, prodCats);
        });
    }
})

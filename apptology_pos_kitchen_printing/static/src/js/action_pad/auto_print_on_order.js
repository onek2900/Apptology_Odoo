/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ActionpadWidget } from "@point_of_sale/app/screens/product_screen/action_pad/action_pad";
import { useService } from "@web/core/utils/hooks";
import { PrinterReceipt } from "../printer_receipt/printer_receipt";

// Keep references to previously patched methods so we can chain them.
const PreviousSetup_KitchenPrinting = ActionpadWidget.prototype.setup;
const PreviousSubmitOrder = ActionpadWidget.prototype.submitOrder;

function getPrintingCategoriesChanges(pos, categories, currentOrderChange) {
    // Filter order lines by printer categories
    return currentOrderChange.filter((line) =>
        pos.db.is_product_in_category(categories, line["product_id"])
    );
}

patch(ActionpadWidget.prototype, {
    setup(...args) {
        if (typeof PreviousSetup_KitchenPrinting === "function") {
            PreviousSetup_KitchenPrinting.apply(this, args);
        }
        this.printer = useService("printer");
    },

    async submitOrder() {
        // Call any existing behavior first (including other modules' patches)
        let result;
        if (PreviousSubmitOrder) {
            result = await PreviousSubmitOrder.apply(this, arguments);
        }

        try {
            // Only auto-print for restaurant POS and when there are changes to print
            const order = this.pos.get_order();
            if (!this.pos.config.module_pos_restaurant || !order) return result;
            if (order.hasChangesToPrint && !order.hasChangesToPrint()) return result;

            // Build a lightweight change set from the order changes when available,
            // otherwise fall back to all orderlines.
            const changes = order.getOrderChanges ? order.getOrderChanges() : null;
            let changeLines = [];
            if (changes && changes.orderlines) {
                // values() because POS returns an object keyed by line uid
                for (const line of Object.values(changes.orderlines)) {
                    const product = (this.pos.db.product_by_id && this.pos.db.product_by_id[line.product_id]) || null;
                    const categories = product ? this.pos.db.get_category_by_id(product.pos_categ_ids) : [];
                    changeLines.push({
                        name: product ? (product.display_name || product.name) : (line.name || ""),
                        note: line.customerNote || line.note,
                        product_id: line.product_id,
                        quantity: line.quantity,
                        category_ids: categories,
                        customerNote: line.customerNote,
                        // topping flags if present from toppings module
                        is_topping: !!(line.is_topping || line.sh_is_topping),
                        is_has_topping: !!(line.is_has_topping || line.sh_is_has_topping),
                        parent_line_id: line.sh_topping_parent ? line.sh_topping_parent.id : null,
                        parent_name: line.sh_topping_parent ? line.sh_topping_parent.full_product_name : null,
                        toppings_count: Array.isArray(line.Toppings) ? line.Toppings.length : (line.Toppings ? 1 : 0),
                    });
                }
            } else {
                // Fallback: include all orderlines
                changeLines = order.orderlines.map((orderline) => ({
                    name: orderline.full_product_name,
                    note: orderline.note,
                    product_id: orderline.product.id,
                    quantity: orderline.quantity,
                    category_ids: this.pos.db.get_category_by_id(orderline.product.pos_categ_ids),
                    customerNote: orderline.customerNote,
                    is_topping: !!(orderline.is_topping || orderline.sh_is_topping),
                    is_has_topping: !!(orderline.is_has_topping || orderline.sh_is_has_topping),
                    parent_line_id: orderline.sh_topping_parent ? orderline.sh_topping_parent.id : null,
                    parent_name: orderline.sh_topping_parent ? orderline.sh_topping_parent.full_product_name : null,
                    toppings_count: Array.isArray(orderline.Toppings) ? orderline.Toppings.length : (orderline.Toppings ? 1 : 0),
                }));
            }

            // Prepare shared header data
            const exported = order.export_for_printing ? order.export_for_printing() : { headerData: {} };

            // Print for each configured kitchen printer with matching categories
            for (const printer of this.pos.unwatched.printers || []) {
                const data = getPrintingCategoriesChanges(this.pos, printer.config.product_categories_ids, changeLines);
                if (!data.length) continue;
                // Optional structured log for debugging
                try {
                    const jsonLog = {
                        type: "kitchen_printer_log",
                        printer: printer.config.name,
                        cashier: exported.headerData?.cashier,
                        order_number: exported.headerData?.trackingNumber,
                        lines: data.map((item) => ({
                            categories: (item.category_ids || []).map((c) => c.name),
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
                    // eslint-disable-next-line no-console
                    console.log(JSON.stringify(jsonLog));
                } catch (_) {}

                // Actual print
                this.printer.print(
                    PrinterReceipt,
                    { data, headerData: exported.headerData, printer },
                    { webPrintFallback: true }
                );
            }
        } catch (e) {
            // eslint-disable-next-line no-console
            console.warn("Auto kitchen print failed", e);
        }
        return result;
    },
});

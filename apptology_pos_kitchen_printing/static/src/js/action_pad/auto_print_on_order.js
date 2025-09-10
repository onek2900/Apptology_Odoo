/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ActionpadWidget } from "@point_of_sale/app/screens/product_screen/action_pad/action_pad";
import { useService } from "@web/core/utils/hooks";
import { PrinterReceipt } from "../printer_receipt/printer_receipt";

// Keep references to previously patched methods so we can chain them.
const PreviousSetup_KitchenPrinting = ActionpadWidget.prototype.setup;
const PreviousSubmitOrder = ActionpadWidget.prototype.submitOrder;

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

function getPrintingCategoriesChanges(pos, printerCategories, currentOrderChange) {
    // Filter order lines by matching category ids (robust to shapes)
    const printerCatIds = normalizeCategoryIds(printerCategories);
    if (!printerCatIds.length) return [];
    const printerCatSet = new Set(printerCatIds);

    function toId(v) {
        if (v == null) return null;
        if (typeof v === "number") return v;
        if (Array.isArray(v)) return toId(v[0]);
        if (typeof v === "object") return toId(v.id ?? v.ID ?? v["_id"]);
        const n = Number(v);
        return Number.isFinite(n) ? n : null;
    }
    function isMatchWithAncestors(catIds) {
        for (const cid of catIds) {
            let cur = toId(cid);
            while (cur) {
                if (printerCatSet.has(cur)) return true;
                const node = pos?.db?.category_by_id?.[cur];
                cur = toId(node?.parent_id);
            }
        }
        return false;
    }

    return currentOrderChange.filter((line) => {
        // Prefer matching against line.category_ids that we computed
        const lineCatIds = normalizeCategoryIds(line.category_ids);
        if (lineCatIds.length) return isMatchWithAncestors(lineCatIds);
        // Fallback: derive from product_id via pos.db
        const product = pos?.db?.product_by_id?.[line.product_id];
        const prodCats = normalizeCategoryIds(product?.pos_categ_ids);
        return isMatchWithAncestors(prodCats);
    });
}

patch(ActionpadWidget.prototype, {
    setup(...args) {
        if (typeof PreviousSetup_KitchenPrinting === "function") {
            PreviousSetup_KitchenPrinting.apply(this, args);
        }
        this.printer = useService("printer");
        // eslint-disable-next-line no-console
        console.log("[kitchen-print] auto_print_on_order setup loaded");
    },

    async submitOrder() {
        // Call any existing behavior first (including other modules' patches)
        let result;
        if (PreviousSubmitOrder) {
            result = await PreviousSubmitOrder.apply(this, arguments);
        }

        try {
            // Baseline debug to confirm our hook runs
            // eslint-disable-next-line no-console
            console.log("[kitchen-print] Order button pressed");
            // Auto-log/print for restaurant POS when pressing Order
            const order = this.pos.get_order();
            if (!order || !this.pos.config?.module_pos_restaurant) return result;

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
            }
            if (!changeLines.length) {
                // Fallback: include all orderlines (ensures logging even when no diff is built)
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
            // Tracking number may already exist on the order even before export
            const orderNumber = order.trackingNumber || exported.headerData?.trackingNumber;

            // Determine printers list across possible locations in POS store
            const printerService = this.printer || this.env?.services?.printer;
            const printers = (this.pos.unwatched && this.pos.unwatched.printers) || this.pos.printers || [];
            if (!Array.isArray(printers) || printers.length === 0) {
                // eslint-disable-next-line no-console
                console.log("[kitchen-print] No kitchen printers configured or loaded");
            } else {
                // eslint-disable-next-line no-console
                console.log("[kitchen-print] Found printers:", printers.map(p => p?.config?.name));
            }

            // Print for each configured kitchen printer with matching categories
            for (const printer of printers) {
                // Verbose dump of categories involved
                try {
                    const pCatIds = normalizeCategoryIds(printer.config.product_categories_ids);
                    const pCatNames = (printer.config.product_categories_ids || [])
                        .map((c) => (typeof c === 'object' && c ? c.name : null))
                        .filter(Boolean);
                    // eslint-disable-next-line no-console
                    console.log(`[kitchen-print] Printer ${printer.config.name} categories`, { ids: pCatIds, names: pCatNames });
                    for (const l of changeLines) {
                        const lIds = normalizeCategoryIds(l.category_ids);
                        const lNames = (l.category_ids || []).map((c) => (c && c.name) || null).filter(Boolean);
                        // eslint-disable-next-line no-console
                        console.log('[kitchen-print] Line categories', { name: l.name, product_id: l.product_id, ids: lIds, names: lNames });
                    }
                } catch (_) {}

                const data = getPrintingCategoriesChanges(this.pos, printer.config.product_categories_ids, changeLines);
                if (!data.length) {
                    // eslint-disable-next-line no-console
                    console.log(`[kitchen-print] No matching lines for printer ${printer.config.name}`);
                    continue;
                }
                // Optional structured log for debugging
                try {
                    const jsonLog = {
                        type: "kitchen_printer_log",
                        printer: printer.config.name,
                        cashier: exported.headerData?.cashier,
                        order_number: orderNumber,
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
                printerService?.print?.(
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

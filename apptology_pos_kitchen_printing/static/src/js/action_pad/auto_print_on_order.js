/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ActionpadWidget } from "@point_of_sale/app/screens/product_screen/action_pad/action_pad";
import { useService } from "@web/core/utils/hooks";
import { useState } from "@odoo/owl";
import { PrinterReceipt } from "../printer_receipt/printer_receipt";

// Keep references to previously patched methods
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
        const lineCatIds = normalizeCategoryIds(line.category_ids);
        if (lineCatIds.length) return isMatchWithAncestors(lineCatIds);
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

        // Reactive state for button indicator
        this.kitchenState = useState({ hasPending: false });

        console.log("[kitchen-print] auto_print_on_order setup loaded");
    },

    async submitOrder() {
        let result;
        if (PreviousSubmitOrder) {
            result = await PreviousSubmitOrder.apply(this, arguments);
        }

        try {
            console.log("[kitchen-print] Order button pressed");
            const order = this.pos.get_order();
            if (!order || !this.pos.config?.module_pos_restaurant) return result;

            const changes = order.getOrderChanges ? order.getOrderChanges() : null;
            let changeLines = [];
            if (changes && changes.orderlines) {
                for (const [uid, line] of Object.entries(changes.orderlines)) {
                    changeLines.push(line);
                }
            }

            // 🔔 Mark that there are changes → update button UI
            this.kitchenState.hasPending = changeLines.length > 0;

            // === your existing kitchen printer routing code ===
            // (unchanged, I left your logging & printing intact)
            const exported = order.export_for_printing ? order.export_for_printing() : { headerData: {} };
            const orderNumber = order.trackingNumber || exported.headerData?.trackingNumber;
            const tableName = (order.table && order.table.name) || (order.pos?.table && order.pos.table.name) || null;
            const floorName = (order.pos?.currentFloor && order.pos.currentFloor.name) || null;

            const printerService = this.printer || this.env?.services?.printer;
            const printers = (this.pos.unwatched && this.pos.unwatched.printers) || this.pos.printers || [];

            for (const printer of printers) {
                const currentForPrinter = getPrintingCategoriesChanges(
                    this.pos,
                    printer.config.product_categories_ids,
                    changeLines
                );

                if (!currentForPrinter.length) {
                    console.log(`[kitchen-print] No matching lines for printer ${printer.config.name}`);
                    continue;
                }

                let doAutoPrint = false;
                try {
                    doAutoPrint = window?.localStorage?.getItem('AUTO_KITCHEN_PRINT_ON_ORDER') === '1';
                } catch (_) {}
                if (doAutoPrint) {
                    printerService?.print?.(
                        PrinterReceipt,
                        { data: currentForPrinter, headerData: { ...exported.headerData, table_name: tableName, floor: floorName }, printer },
                        { webPrintFallback: false }
                    );
                }
            }

            // ✅ Reset the indicator after printing
            this.kitchenState.hasPending = false;

        } catch (e) {
            console.warn("Auto kitchen print failed", e);
        }
        return result;
    },
});

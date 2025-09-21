/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ActionpadWidget } from "@point_of_sale/app/screens/product_screen/action_pad/action_pad";
import { useService } from "@web/core/utils/hooks";
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
    async setup() {
        if (PreviousSetup_KitchenPrinting) {
            PreviousSetup_KitchenPrinting.apply(this, arguments);
        }
        this.printer = useService("printer");
    },

    async submitOrder() {
        const order = this.pos.get_order();
        if (!order) {
            return PreviousSubmitOrder.apply(this, arguments);
        }

        const printers = (this.pos.unwatched && this.pos.unwatched.printers) || this.pos.printers || [];
        if (!Array.isArray(printers) || printers.length === 0) {
            console.log("[kitchen-print] No kitchen printers configured or loaded");
            return PreviousSubmitOrder.apply(this, arguments);
        }

        // Track lines
        const curLinesMap = new Map();
        for (const ol of order.orderlines) {
            const product = ol.product || (this.pos.db.product_by_id && this.pos.db.product_by_id[ol.product?.id]);
            const categories = product ? this.pos.db.get_category_by_id(product.pos_categ_ids) : [];
            const lineUid = ol.uid || ol.cid || `${ol.product?.id || ''}|${ol.full_product_name || ''}`;
            curLinesMap.set(lineUid, {
                uid: lineUid,
                name: ol.full_product_name || (product ? (product.display_name || product.name) : (ol.name || "")),
                note: ol.customerNote || ol.note,
                product_id: ol.product?.id,
                quantity: ol.quantity,
                category_ids: categories,
            });
        }

        // Loop through printers
        for (const printer of printers) {
            const currentForPrinter = getPrintingCategoriesChanges(
                this.pos,
                printer.config.product_categories_ids,
                Array.from(curLinesMap.values())
            );

            const data = [];
            for (const item of currentForPrinter) {
                const uid = item.uid || `${item.product_id || ''}|${item.name || ''}`;
                const qty = Number(item.quantity || 0);
                if (qty > 0) {
                    data.push({ ...item, quantity: qty });
                }
            }

            if (!data.length) {
                console.log(`[kitchen-print] No items matched printer categories for ${printer.config.name}`);
                continue;   // ✅ Skip printing, but don’t block the order
            }

            try {
                await this.printer.print(PrinterReceipt, {
                    data,
                    headerData: order.export_for_printing().headerData,
                    printer,
                });
            } catch (err) {
                console.error("[kitchen-print] Error printing:", err);
            }
        }

        // ✅ Always submit the order, even if no printer printed anything
        return await PreviousSubmitOrder.apply(this, arguments);
    },
});
/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { Order } from "@point_of_sale/app/store/models";

const previousHasChangesToPrint = Order.prototype.hasChangesToPrint;

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

function hasLineOutsidePrinterCategories(order, printers) {
    if (!order?.orderlines?.length) {
        return false;
    }
    const productById = order.pos?.db?.product_by_id || {};
    for (const line of order.orderlines) {
        if (!line) continue;
        const quantity = typeof line.get_quantity === "function" ? line.get_quantity() : line.quantity;
        if (!quantity) {
            continue;
        }
        const product = line.product || productById?.[line.product?.id];
        const lineCatIds = normalizeCategoryIds(product?.pos_categ_ids);
        let matched = false;
        for (const printer of printers) {
            const printerCatIds = normalizeCategoryIds(printer?.config?.product_categories_ids);
            if (!printerCatIds.length) {
                matched = true;
                break;
            }
            for (const catId of lineCatIds) {
                if (printerCatIds.includes(catId)) {
                    matched = true;
                    break;
                }
            }
            if (matched) {
                break;
            }
        }
        if (!matched) {
            return true;
        }
    }
    return false;
}

patch(Order.prototype, {
    hasChangesToPrint(...args) {
        const result = previousHasChangesToPrint
            ? previousHasChangesToPrint.apply(this, args)
            : false;
        if (result) {
            return result;
        }
        if (!this.pos?.config?.module_pos_restaurant) {
            return result;
        }
        const printers = this.pos?.unwatched?.printers || this.pos?.printers || [];
        if (!Array.isArray(printers)) {
            return result;
        }
        if (!printers.length) {
            return this.orderlines?.length ? true : result;
        }
        if (hasLineOutsidePrinterCategories(this, printers)) {
            return true;
        }
        return result;
    },
});

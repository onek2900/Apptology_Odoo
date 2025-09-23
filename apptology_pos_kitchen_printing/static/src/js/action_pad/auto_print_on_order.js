/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ActionpadWidget } from "@point_of_sale/app/screens/product_screen/action_pad/action_pad";
import { useService } from "@web/core/utils/hooks";
import { PrinterReceipt } from "../printer_receipt/printer_receipt";

// Keep references to previously patched methods so we can chain them.
const PreviousSetup_KitchenPrinting = ActionpadWidget.prototype.setup;
const PreviousSubmitOrder = ActionpadWidget.prototype.submitOrder;
const PreviousDisableOrderDescriptor = Object.getOwnPropertyDescriptor(
    ActionpadWidget.prototype,
    "disableOrder"
);
const PreviousDisableOrder = PreviousDisableOrderDescriptor?.get;

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
    if (!printerCatIds.length) return []; // instead of []  
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


function normalizeBooleanFlag(value) {
    if (Array.isArray(value)) {
        return value.some((item) => normalizeBooleanFlag(item));
    }
    if (value === undefined || value === null) {
        return false;
    }
    if (typeof value === 'string') {
        const normalized = value.trim().toLowerCase();
        if (!normalized) {
            return false;
        }
        if (['false', '0', 'no', 'off', 'n'].includes(normalized)) {
            return false;
        }
        if (['true', '1', 'yes', 'on', 'y'].includes(normalized)) {
            return true;
        }
        return Boolean(value);
    }
    if (typeof value === 'number') {
        return value !== 0;
    }
    if (typeof value === 'boolean') {
        return value;
    }
    return Boolean(value);
}

function extractToppingFlags(line, product) {
    const lineFlag = normalizeBooleanFlag(line && line.sh_is_topping);
    const productFlag = normalizeBooleanFlag(product && product.sh_is_topping);
    const hasFlag = normalizeBooleanFlag(line && line.sh_is_has_topping);
    return {
        sh_is_topping: lineFlag || productFlag,
        sh_is_has_topping: hasFlag,
    };
}

function resolveOrderline(order, line, fallbackUid) {
    if (!order) {
        return null;
    }
    const candidates = [
        line && line.uid,
        line && line.uuid,
        line && line.id,
        fallbackUid
    ].filter(Boolean);
    for (const identifier of candidates) {
        const match = order.orderlines.find((ol) =>
            ol && (
                ol.uid === identifier ||
                ol.id === identifier ||
                ol.cid === identifier ||
                ol.uuid === identifier
            )
        );
        if (match) {
            return match;
        }
    }
    return null;
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

            // Build a lightweight change set from the order changes when available.
            // Additionally, prepare a snapshot of current orderlines so we can
            // detect quantity increments even if another module reset the
            // 'last change' baseline before our hook runs.
            const changes = order.getOrderChanges ? order.getOrderChanges() : null;
            let changeLines = [];
            if (changes && changes.orderlines) {
                // entries() to capture the line uid (key)
                for (const [uid, line] of Object.entries(changes.orderlines)) {
                    const product = (this.pos.db.product_by_id && this.pos.db.product_by_id[line.product_id]) || null;
                    const categories = product ? this.pos.db.get_category_by_id(product.pos_categ_ids) : [];
                    const uidHint = line.uid || line.uuid || uid;
                    const resolvedLine = resolveOrderline(order, line, uidHint) || null;
                    const flags = extractToppingFlags(resolvedLine || line, product);
                    changeLines.push({
                        uid: uidHint,
                        name: resolvedLine ? resolvedLine.full_product_name || resolvedLine.product?.display_name || resolvedLine.product?.name || resolvedLine.name || '' : (product ? (product.display_name || product.name) : (line.name || '')),
                        note: resolvedLine ? resolvedLine.customerNote || resolvedLine.note : (line.customerNote || line.note),
                        product_id: resolvedLine ? resolvedLine.product?.id || line.product_id : line.product_id,
                        quantity: resolvedLine ? resolvedLine.quantity : line.quantity,
                        category_ids: categories,
                        customerNote: resolvedLine ? resolvedLine.customerNote || resolvedLine.note : line.customerNote,
                        sh_is_topping: flags.sh_is_topping,
                        sh_is_has_topping: flags.sh_is_has_topping,
                        parent_line_id: (resolvedLine && resolvedLine.sh_topping_parent ? resolvedLine.sh_topping_parent.id : null) || (line.sh_topping_parent ? line.sh_topping_parent.id : null),
                        parent_name: (resolvedLine && resolvedLine.sh_topping_parent ? resolvedLine.sh_topping_parent.full_product_name : null) || (line.sh_topping_parent ? line.sh_topping_parent.full_product_name : null),
                        toppings_count: resolvedLine ? (Array.isArray(resolvedLine.Toppings) ? resolvedLine.Toppings.length : (resolvedLine.Toppings ? 1 : 0)) : (Array.isArray(line.Toppings) ? line.Toppings.length : (line.Toppings ? 1 : 0)),
                    });
                }
            }

            // Snapshot of current order lines keyed for stable tracking
            const curLinesMap = new Map();
            try {
                for (const ol of order.orderlines) {
                    const product = ol.product || (this.pos.db.product_by_id && this.pos.db.product_by_id[ol.product?.id]);
                    const categories = product ? this.pos.db.get_category_by_id(product.pos_categ_ids) : [];
                    const lineUid = ol.uid || ol.cid || `${ol.product?.id || ''}|${ol.full_product_name || ol.product?.display_name || ol.product?.name || ''}|${ol.note || ol.customerNote || ''}|${ol.sh_topping_parent ? ol.sh_topping_parent.id : ''}`;
                    const key = lineUid;
                    const flags = extractToppingFlags(ol, product);
                    curLinesMap.set(key, {
                        uid: lineUid,
                        name: ol.full_product_name || (product ? (product.display_name || product.name) : (ol.name || "")),
                        note: ol.customerNote || ol.note,
                        product_id: ol.product?.id,
                        quantity: ol.quantity,
                        category_ids: categories,
                        customerNote: ol.customerNote,
                        sh_is_topping: flags.sh_is_topping,
                        sh_is_has_topping: flags.sh_is_has_topping,
                        parent_line_id: ol.sh_topping_parent ? ol.sh_topping_parent.id : null,
                        parent_name: ol.sh_topping_parent ? ol.sh_topping_parent.full_product_name : null,
                        toppings_count: Array.isArray(ol.Toppings) ? ol.Toppings.length : (ol.Toppings ? 1 : 0),
                    });
                }
            } catch (_) {}
            if (!changeLines.length) {
                // Fallback: include all orderlines (ensures logging even when no diff is built)
                changeLines = order.orderlines.map((orderline) => {
                    const flags = extractToppingFlags(orderline, orderline.product);
                    return ({
                        name: orderline.full_product_name,
                        note: orderline.note,
                        product_id: orderline.product.id,
                        quantity: orderline.quantity,
                        category_ids: this.pos.db.get_category_by_id(orderline.product.pos_categ_ids),
                        customerNote: orderline.customerNote,
                        uid: orderline.uid || orderline.cid || `${orderline.product?.id || ''}|${orderline.full_product_name || orderline.product?.display_name || orderline.product?.name || ''}|${orderline.note || orderline.customerNote || ''}|${orderline.sh_topping_parent ? orderline.sh_topping_parent.id : ''}`,
                        sh_is_topping: flags.sh_is_topping,
                        sh_is_has_topping: flags.sh_is_has_topping,
                        parent_line_id: orderline.sh_topping_parent ? orderline.sh_topping_parent.id : null,
                        parent_name: orderline.sh_topping_parent ? orderline.sh_topping_parent.full_product_name : null,
                        toppings_count: Array.isArray(orderline.Toppings) ? orderline.Toppings.length : (orderline.Toppings ? 1 : 0),
                    });
                });
            }

            // Prepare shared header data
            const exported = order.export_for_printing ? order.export_for_printing() : { headerData: {} };
            // Tracking number may already exist on the order even before export
            const orderNumber = order.trackingNumber || exported.headerData?.trackingNumber;
            const tableName = (order.table && order.table.name) || (order.pos?.table && order.pos.table.name) || null;
            const floorName = (order.pos?.currentFloor && order.pos.currentFloor.name) || null;

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

                // Per-printer already-emitted tracker on the order to avoid duplicates
                const printerKey = printer.config?.id || printer.config?.name || "__unknown";
                order.__kitchenPrintedByPrinter = order.__kitchenPrintedByPrinter || {};
                const printedMap = (order.__kitchenPrintedByPrinter[printerKey] = order.__kitchenPrintedByPrinter[printerKey] || {});

                // Filter by printer categories first using the full current snapshot
                // Keep per-line uids so we can emit each new line separately
                const currentForPrinter = getPrintingCategoriesChanges(
                    this.pos,
                    printer.config.product_categories_ids,
                    Array.from(curLinesMap.values())
                );
                // Per-printer, per-line-uid tracker. This ensures identical items on
                // different lines are emitted separately, while quantity increments
                // on the same line uid produce a delta quantity.
                order.__kitchenPrintedUidByPrinter = order.__kitchenPrintedUidByPrinter || {};
                const printedUidMap = (order.__kitchenPrintedUidByPrinter[printerKey] =
                    order.__kitchenPrintedUidByPrinter[printerKey] || {});

                // Build delta per line uid
                const data = [];
                for (const item of currentForPrinter) {
                    const uid = item.uid || `${item.product_id || ''}|${item.name || ''}|${item.note || ''}|${item.parent_line_id || ''}`;
                    const already = Number(printedUidMap[uid] || 0);
                    const qty = Number(item.quantity || 0);
                    const diff = qty - already;
                    if (diff > 0) {
                        data.push({ ...item, quantity: diff });
                    }
                }
                if (!data.length) {
                    // eslint-disable-next-line no-console
                    console.log(`[kitchen-print] No matching lines for printer ${printer.config.name}`);
                    continue;
                }
                // Optional structured log for debugging
                try {
                    const tableName = (order.table && order.table.name) || (order.pos?.table && order.pos.table.name) || null;
                    const floorName = (order.pos?.currentFloor && order.pos.currentFloor.name) || null;
                    const jsonLog = {
                        type: "kitchen_printer_log",
                        source: "pos",
                        printer: printer.config.name,
                        cashier: exported.headerData?.cashier,
                        order_number: orderNumber,
                        table_name: tableName,
                        floor: floorName,
                        lines: data.map((item) => ({
                            categories: (item.category_ids || []).map((c) => c.name),
                            name: item.name,
                            qty: item.quantity,
                            note: item.customerNote,
                            sh_is_topping: !!item.sh_is_topping,
                            sh_is_has_topping: !!item.sh_is_has_topping,
                            parent_line_id: item.parent_line_id || null,
                            parent_name: item.parent_name || null,
                            toppings_count: item.toppings_count || 0,
                        })),
                    };
                    // eslint-disable-next-line no-console
                    console.log(JSON.stringify(jsonLog));
                } catch (_) {}

                // Optional physical print: disabled by default to avoid popping the browser print dialog.
                // Enable by setting localStorage AUTO_KITCHEN_PRINT_ON_ORDER=1
                let doAutoPrint = false;
                try {
                    doAutoPrint = window?.localStorage?.getItem('AUTO_KITCHEN_PRINT_ON_ORDER') === '1';
                } catch (_) {}
                if (doAutoPrint) {
                    printerService?.print?.(
                        PrinterReceipt,
                        { data, headerData: { ...exported.headerData, table_name: tableName, floor: floorName }, printer },
                        { webPrintFallback: false }
                    );
                }

                // Update per-uid tracker to current quantities
                for (const item of currentForPrinter) {
                    const uid = item.uid || `${item.product_id || ''}|${item.name || ''}|${item.note || ''}|${item.parent_line_id || ''}`;
                    printedUidMap[uid] = Number(item.quantity || 0);
                }
            }
        } catch (e) {
            // eslint-disable-next-line no-console
            console.warn("Auto kitchen print failed", e);
        }
        return result;
    },
});

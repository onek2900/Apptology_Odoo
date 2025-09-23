/** @odoo-module **/
import { ReceiptScreen } from "@point_of_sale/app/screens/receipt_screen/receipt_screen";
import { patch } from "@web/core/utils/patch";
import { PrinterReceipt } from "../printer_receipt/printer_receipt"
import { useRef } from "@odoo/owl";



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
    const lineFlag = normalizeBooleanFlag(line && (line.sh_is_topping ?? line.is_topping));
    const hasFlag = normalizeBooleanFlag(line && (line.sh_is_has_topping ?? line.is_has_topping));
    const productFlag = normalizeBooleanFlag(product && product.sh_is_topping);
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
        line && line.id,
        line && line.uid,
        line && line.uuid,
        fallbackUid
    ].filter(Boolean);
    for (const identifier of candidates) {
        const match = order.orderlines.find((ol) => ol && (
            ol.id === identifier ||
            ol.uid === identifier ||
            ol.cid === identifier ||
            ol.uuid === identifier
        ));
        if (match) {
            return match;
        }
    }
    return null;
}

function toPlainLine(orderline, product, fallbackUid) {
    if (!orderline) {
        return null;
    }
    const categories = product ? this.pos.db.get_category_by_id(product.pos_categ_ids) : [];
    const flags = extractToppingFlags(orderline, product);
    return {
        name: orderline.full_product_name || (product ? (product.display_name || product.name) : (orderline.name || '')),
        note: orderline.customerNote || orderline.note,
        product_id: orderline.product?.id,
        quantity: orderline.quantity,
        category_ids: categories,
        customerNote: orderline.customerNote,
        uid: orderline.uid || orderline.cid || fallbackUid || `${orderline.product?.id || ''}|${orderline.full_product_name || orderline.product?.display_name || orderline.product?.name || ''}|${orderline.note || orderline.customerNote || ''}|${orderline.sh_topping_parent ? orderline.sh_topping_parent.id : ''}`,
        sh_is_topping: flags.sh_is_topping,
        sh_is_has_topping: flags.sh_is_has_topping,
        parent_line_id: orderline.sh_topping_parent ? orderline.sh_topping_parent.id : null,
        parent_name: orderline.sh_topping_parent ? orderline.sh_topping_parent.full_product_name : null,
        toppings_count: Array.isArray(orderline.Toppings) ? orderline.Toppings.length : (orderline.Toppings ? 1 : 0),
    };
}

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
        // Only include newly added/changed lines (not the whole order)
        const changes = order.getOrderChanges ? order.getOrderChanges() : null;
        let lines = [];
        if (changes && changes.orderlines) {
            for (const [uid, ch] of Object.entries(changes.orderlines)) {
                const product = this.pos.db.product_by_id?.[ch.product_id];
                const resolved = resolveOrderline(order, ch, uid);
                const plain = toPlainLine.call(this, resolved || ch, product, uid);
                if (plain) {
                    lines.push(plain);
                }
            }
        }
        if (!lines.length) {
            lines = order.orderlines.map((ol) => {
                const product = this.pos.db.product_by_id?.[ol.product?.id] || ol.product;
                return toPlainLine.call(this, ol, product, null);
            }).filter(Boolean);
        }

        for (const printer of this.pos.unwatched.printers) {
            const data = this._getPrintingCategoriesChanges(
                printer.config.product_categories_ids,
                lines,
            );
            if (data.length > 0) {
                const printerName = printer.config.name;
                const exported = order.export_for_printing();
                const cashierName = exported.headerData?.cashier;
                const orderNumber = exported.headerData?.trackingNumber;
                const tableName = (order.table && order.table.name) || (order.pos?.table && order.pos.table.name) || null;
                const floorName = (order.pos?.currentFloor && order.pos.currentFloor.name) || null;

                // Build a single structured JSON log per printer
                const jsonLog = {
                    type: "kitchen_printer_log",
                    source: "pos",
                    printer: printerName,
                    cashier: cashierName,
                    order_number: orderNumber,
                    table_name: tableName,
                    floor: floorName,
                    lines: data.map((item) => ({
                        categories: item.category_ids.map((cat) => cat.name),
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
                    const node = this.pos?.db?.category_by_id?.[cur];
                    cur = toId(node?.parent_id);
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


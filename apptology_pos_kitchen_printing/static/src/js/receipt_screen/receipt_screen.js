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
        // Only include newly added/changed lines (not the whole order)
        const changes = order.getOrderChanges ? order.getOrderChanges() : null;
        let lines = [];
        if (changes && changes.orderlines) {
            for (const ch of Object.values(changes.orderlines)) {
                const product = this.pos.db.product_by_id?.[ch.product_id];
                lines.push({
                    name: product ? (product.display_name || product.name) : (ch.name || ""),
                    note: ch.customerNote || ch.note,
                    product_id: ch.product_id,
                    quantity: ch.quantity,
                    category_ids: product ? this.pos.db.get_category_by_id(product.pos_categ_ids) : [],
                    customerNote: ch.customerNote,
                    // flags and parent linkage (when available from toppings module)
                    is_topping: !!(ch.is_topping || ch.sh_is_topping),
                    is_has_topping: !!(ch.is_has_topping || ch.sh_is_has_topping),
                    parent_line_id: ch.sh_topping_parent ? ch.sh_topping_parent.id : null,
                    parent_name: ch.sh_topping_parent ? ch.sh_topping_parent.full_product_name : null,
                    toppings_count: Array.isArray(ch.Toppings) ? ch.Toppings.length : (ch.Toppings ? 1 : 0),
                });
            }
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
                const tableId = (order.table && order.table.id) || (order.pos?.table && order.pos.table.id) || null;
                const floorName = (order.pos?.currentFloor && order.pos.currentFloor.name) || null;

                // Build a single structured JSON log per printer
                const jsonLog = {
                    type: "kitchen_printer_log",
                    source: "pos",
                    printer: printerName,
                    cashier: cashierName,
                    order_number: orderNumber,
                    table_id: tableId,
                    floor: floorName,
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

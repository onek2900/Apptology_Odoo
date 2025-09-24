/** @odoo-module */

import { usePos } from "@point_of_sale/app/store/pos_hook";
import { registry } from "@web/core/registry";
import { Component,useState,onWillUnmount } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { ConfirmPopup } from "@point_of_sale/app/utils/confirm_popup/confirm_popup";
import { _t } from "@web/core/l10n/translation";
import { onlineOrderReceipt } from "./online_order_receipt";

export class OnlineOrderScreen extends Component {
    static template = "point_of_sale.OnlineOrderScreen";
    setup() {
        this.pos = usePos();
        this.orm = useService("orm");
        this.rpc = useService("rpc");
        this.popup = useService("popup");
        this.printer = useService("printer");
        this.state = useState({
            clickedOrder: {},
            orders: [],
            currency_symbol: this.env.services.pos.currency.symbol,
            isAutoApprove: this.pos.config.auto_approve,
            // Filters and paging
            filters: {
                datePreset: 'today', // today | yesterday | 7d | month
                status: 'all', // all | open | paid | refunded | cancelled
                source: 'all', // all | online | pos
                query: '',
            },
            page: 1,
            hasMore: false,
            loading: false,
        });
        this.channel=`new_pos_order_${this.pos.config.id}`;
        this.busService = this.env.services.bus_service;
        this.busService.addChannel(this.channel);
        this._busHandler = ({ detail: notifications }) => {
            try {
                const filtered = (notifications || []).filter((n) => n?.payload?.channel === this.channel);
                for (const n of filtered) {
                    this.reloadOrders();
                }
            } catch (e) {
                console.warn('Online order bus handler failed', e);
            }
        };
        this.busService.addEventListener('notification', this._busHandler);
        this.initiateServices();
        onWillUnmount(()=>{
            if (this.pollingInterval) clearInterval(this.pollingInterval);
            if (this._busHandler) this.busService.removeEventListener('notification', this._busHandler);
        })
    }
    /**
     * Initiates services by fetching open orders and starting polling.
     */
    async initiateServices(){
        this.reloadOrders();
        this.startPollingOrders();
    }
    /**
     * To get time only from datetime
     */
    formatTime(dateStr) {
    const date = new Date(dateStr);
    const time = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit',second: '2-digit'  });
    const formattedDate = date.toLocaleDateString('en-CA'); // YYYY-MM-DD
    return {
        time: time,
        date: formattedDate,
    };
}
    /**
     * Auto receipt printing
     */
   async printReceipt(order) {
        try {
        const [exportedOrder] = await this.orm.call("pos.order", "export_order_for_ui", [order]);
        if (!exportedOrder) {
            console.error("No order data returned from backend.");
            return;
        }
        if (exportedOrder) {
        const cashierName = exportedOrder.headerData?.cashier || "N/A";
        const orderNumber = exportedOrder.headerData?.trackingNumber || "N/A";

        // Helper utilities for category filtering (mirror kitchen printing logic)
        const normalizeCategoryIds = (cats) => {
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
        };
        const toId = (v) => {
            if (v == null) return null;
            if (typeof v === "number") return v;
            if (Array.isArray(v)) return toId(v[0]);
            if (typeof v === "object") return toId(v.id ?? v.ID ?? v["_id"]);
            const n = Number(v);
            return Number.isFinite(n) ? n : null;
        };
        const productMatchesPrinter = (product, printerCatsSet) => {
            if (!product) return false;
            const cats = normalizeCategoryIds(product.pos_categ_ids);
            for (const cid of cats) {
                let cur = toId(cid);
                while (cur) {
                    if (printerCatsSet.has(cur)) return true;
                    const node = this.pos?.db?.category_by_id?.[cur];
                    cur = toId(node?.parent_id);
                }
            }
            return false;
        };

        // Emit one structured JSON log per printer (unified type + source)
        for (const printer of this.pos.unwatched.printers) {
            const printerName = printer.config.name;
            const pCatIds = normalizeCategoryIds(printer.config.product_categories_ids);
            const pCatSet = new Set(pCatIds);

            // Build per-printer lines filtered by product categories
            const linesForPrinter = [];
            exportedOrder.lines.forEach((lineArr) => {
                const line = lineArr && lineArr[2];
                if (!line) return;
                const pid = toId(line.product_id);
                const product = pid ? this.pos.db.product_by_id?.[pid] : null;
                if (!productMatchesPrinter(product, pCatSet)) return;
                const rawTop = line.sh_is_topping;
                const isTopping = Array.isArray(rawTop) ? !!rawTop[0] : !!rawTop;
                const rawHas = line.sh_is_has_topping;
                const isHasTopping = Array.isArray(rawHas) ? !!rawHas[0] : !!rawHas;
                // Build categories names for convenience
                const catObjs = product ? this.pos.db.get_category_by_id(product.pos_categ_ids) : [];
                const catNames = (catObjs || []).map((c) => c && c.name).filter(Boolean);
                linesForPrinter.push({
                    categories: catNames,
                    name: line.full_product_name,
                    qty: line.qty,
                    note: line.note || "",
                    sh_is_topping: isTopping,
                    sh_is_has_topping: isHasTopping,
                });
            });

            if (linesForPrinter.length === 0) continue;

            const jsonLog = {
                type: "kitchen_printer_log",
                source: "online",
                printer: printerName,
                cashier: cashierName,
                order_number: orderNumber,
                table_id: null,
                floor: null,
                lines: linesForPrinter,
            };
            try {
                console.log(JSON.stringify(jsonLog));
            } catch (e) {
                console.warn("Failed to stringify kitchen printer log (online)", e);
            }
        }
    }
        const currentOrder = this.pos.pos_orders.find(o => o.id === order);
        const orderLines = [];
        exportedOrder.lines.forEach(lineArr => {
            const line = lineArr[2];
            if (line && line.id) {
                const shIsToppingRaw = line.sh_is_topping;
                const isTopping = Array.isArray(shIsToppingRaw)
                    ? !!shIsToppingRaw[0]
                    : !!shIsToppingRaw;
                orderLines.push({
                    lineId: line.id,
                    name: line.full_product_name,
                    qty: line.qty,
                    note: line.note,
                    sh_is_topping: isTopping,
                });
            }
        });
        const safeData = {
            ...(exportedOrder || {}),
            orderData: currentOrder || exportedOrder || {},
            orderLineData: orderLines,
            headerData: { company: this.pos.company },
        };
        try {
            const curOrder = this.pos && typeof this.pos.get_order === 'function' ? this.pos.get_order() : null;
            if (curOrder) {
                curOrder.is_reciptScreen = true;
            }
        } catch (e) {
            // No active POS order; proceed with printing
        }
        this.printer.print(
            onlineOrderReceipt,
            {
                data: safeData,
                formatCurrency: this.env.utils.formatCurrency,
            },
            { webPrintFallback: true }
        );
    } catch (error) {
        console.error("Failed to print online order receipt:", error);
    }
}
    /**
     * Fetch orders with current filters and page.
     */
    async fetchOrders(page = 1){
        // Coalesce overlapping requests to avoid race-induced duplicates
        this._reqToken = (this._reqToken || 0) + 1;
        const reqToken = this._reqToken;
        this.state.loading = true;
        try {
            const payload = {
                config_id: this.pos.config.id,
                filters: {
                    date_preset: this.state.filters.datePreset,
                    status: this.state.filters.status,
                    source: this.state.filters.source,
                    query: this.state.filters.query,
                },
                page: page,
                page_size: 50,
            }
            const result = await this.orm.call("pos.order", "get_orders", [], payload);

            // Ignore stale responses
            if (reqToken !== this._reqToken) return;

            const incoming = Array.isArray(result?.orders) ? result.orders : [];
            const existing = page === 1 ? [] : (Array.isArray(this.state.orders) ? this.state.orders : []);
            // Merge and de-duplicate by id, preserving newest-first order
            const seen = new Set();
            const merged = [];
            for (const o of [...incoming, ...existing]) {
                const oid = (o && (typeof o.id === 'number' ? o.id : Number(o.id))) || null;
                if (!oid || seen.has(oid)) continue;
                seen.add(oid);
                merged.push(o);
            }
            this.state.orders = merged;
            this.state.page = page;
            this.state.hasMore = !!result.has_more;
        } catch (error) {
            console.error("Error fetching orders:", error);
        } finally {
            this.state.loading = false;
        }
    }

    async reloadOrders(){
        await this.fetchOrders(1);
    }

    async loadMore(){
        if (this.state.hasMore && !this.state.loading){
            await this.fetchOrders(this.state.page + 1);
        }
    }
    /**
     * Starts polling for open orders every 10 seconds.
     */
    async startPollingOrders() {
        this.pollingInterval = setInterval(async () => this.reloadOrders(), 10000);
    }
    /**
     * Approves an online order.
     *
     * @param {number} orderId - The ID of the order to approve.
     */
    async onApproveOrder(orderId) {
       this.printReceipt(orderId)
        await this.orm.call(
            "pos.order",
            "update_order_status",
            [orderId],
            { status: 'approved'},
        );
        this.env.bus.trigger('online_order_state_update');
        this.reloadOrders();
    }
    /**
     * Declines an online order after confirmation.
     *
     * @param {number} orderId - The ID of the order to decline.
     */
    async onDeclineOrder(orderId) {
        const {confirmed} =  await this.popup.add(ConfirmPopup, {
            title: _t("Confirmation"),
            body: _t(
                "Are you sure you want to cancel the order ?"
            ),
        });
        if (confirmed){
                await this.orm.call(
                        "pos.order",
                        "update_order_status",
                        [orderId],
                        { status: 'declined'},
                        )
                this.env.bus.trigger('online_order_state_update');
                this.reloadOrders();
            }
    }
    /**
    * Ready function to make the order stage ready
    */
    async done_order(order){
        try {
            const toId = (v) => {
                if (v == null) return null;
                if (typeof v === 'number') return v;
                if (Array.isArray(v)) return toId(v[0]);
                if (typeof v === 'object') return toId(v.id ?? v.ID ?? v._id);
                const n = Number(v);
                return Number.isFinite(n) ? n : null;
            };
            // Read fresh line ids from server to avoid stale/embedded structures
            const recs = await this.orm.read('pos.order', [toId(order.id)], ['lines']);
            const liveLineIds = Array.isArray(recs) && recs[0] && Array.isArray(recs[0].lines) ? recs[0].lines : [];
            // Fetch line details to filter out modifiers/toppings
            const lineDetails = liveLineIds.length
                ? await this.orm.read('pos.order.line', liveLineIds, ['id','order_status','sh_is_topping','product_sh_is_topping'])
                : [];
            const toBool = (v) => {
                if (Array.isArray(v)) return v.length ? !!v[0] : false;
                if (typeof v === 'string') return ['1','true','yes','on','y'].includes(v.trim().toLowerCase());
                return !!v;
            };
            const isModifier = (ld) => toBool(ld?.sh_is_topping) || toBool(ld?.product_sh_is_topping);
            const mainLineIds = (lineDetails || [])
                .filter((ld) => ld && !isModifier(ld))
                .map((ld) => toId(ld.id))
                .filter((id) => typeof id === 'number');

            if (mainLineIds.length) {
                // Mark main lines as ready in the kitchen screen (endpoint toggles; these are non-ready lines)
                // Filter to only non-ready lines to avoid flipping ready -> waiting
                const nonReadyIds = (lineDetails || [])
                    .filter((ld) => ld && !isModifier(ld) && String(ld.order_status) !== 'ready')
                    .map((ld) => toId(ld.id))
                    .filter((id) => typeof id === 'number');
                const validIds = nonReadyIds.filter((id) => typeof id === 'number' && id > 0);
                if (validIds.length) {
                    await this.rpc("/pos/kitchen/line_status", { line_ids: validIds });
                }
            }

            // Recompute and persist the order readiness on the server
            await this.rpc("/pos/kitchen/order_status", {
                method: 'order_progress_change',
                order_id: Number(order.id),
            });

            if (order) {
                order.order_status = 'ready';
            }
        } catch (e) {
            console.error('Failed to mark order ready in kitchen screen:', e);
        }
    }
    /**
     * Closes the online order screen and navigates to the product screen.
     */
    closeOnlineOrderScreen(){
        const pos = this.env.services.pos;
        try {
            if (!pos.get_order()) {
                pos.add_new_order();
            }
        } catch (e) {
            console.warn('Failed to ensure a current order before returning to ProductScreen:', e);
        }
        pos.showScreen("ProductScreen");
    }
    // Ensure topping modifiers carry a consistent boolean flag for styling.
    normalizeOrderLines(lines){
        if (!Array.isArray(lines)){
            return [];
        }
        return lines.map((line) => {
            if (!line){
                return line;
            }
            const normalizedLine = { ...line };
            const rawTopping = normalizedLine.sh_is_topping;
            const normalizedSh = Array.isArray(rawTopping) ? !!rawTopping[0] : !!rawTopping;
            normalizedLine.sh_is_topping = normalizedSh;
            return normalizedLine;
        });
    }

    /**
     * Updates the clicked order state to show its details.
     *
     * @param {Object} order - The order object that was clicked.
     */
    onClickOrder(order){
        if (!order){
            this.state.clickedOrder = {};
            return;
        }
        const normalizedLines = this.normalizeOrderLines(order.lines);
        this.state.clickedOrder = {
            ...order,
            lines: normalizedLines,
        };
    }
    /**
     * Finalizes an online order.
     *
     * @param {Object} order - The order object to finalize.
     */
    async finalizeOrder(order){
        await this.orm.call("pos.order", "update_order_status", [order.id],{status:'finalized'});
        this.state.clickedOrder = {};
        this.reloadOrders();
    }
    /**
     * Redirects to the ticket screen when an order is double-clicked.
     *
     * @param {Object} order - The order object that was double-clicked.
     */
    async onDoubleClick(order){
        if (order.online_order_status && ['approved', 'finalized'].includes(order.online_order_status)){
            const searchDetails = {
                fieldName: "RECEIPT_NUMBER",
                searchTerm: order.pos_reference,
            };
            const ticketFilter = order.state=='paid'?"SYNCED":"ACTIVE_ORDERS";
            // Do not pre-sync here; TicketScreen will handle loading to avoid duplicate fetches
            this.pos.showScreen("TicketScreen", {
                ui: { filter: ticketFilter, searchDetails },
            });
        }
    }
}
registry.category("pos_screens").add("OnlineOrderScreen", OnlineOrderScreen);

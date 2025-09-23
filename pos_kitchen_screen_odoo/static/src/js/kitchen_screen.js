/** @odoo-module */

import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";
const {DateTime} = luxon;
import { Component, onWillStart, useState, onMounted, onWillUnmount, whenReady, App } from "@odoo/owl";
import { makeEnv, startServices } from "@web/env";
import { templates } from "@web/core/assets";
import { _t } from "@web/core/l10n/translation";
import { session } from "@web/session";

// Constants for order statuses
const ORDER_STATUSES = {
    DRAFT: 'draft',
    WAITING: 'waiting',
    READY: 'ready',
    CANCEL: 'cancel'
};

// Constants for bus events
const BUS_CHANNEL = "pos_order_created";
const BUS_EVENT = {
    MESSAGE: "pos_order_created",
    MODEL: "pos.order"
};

const normalizeBooleanFlag = (value) => {
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
};

const computeModifierFlag = (line) => {
    if (!line) {
        return false;
    }
    const primary = normalizeBooleanFlag(line.sh_is_topping);
    const fallback = normalizeBooleanFlag(line.is_topping);
    return primary || fallback;
};

/**
 * Custom hook for order management functionality
 * @param {Object} rpc - ORM service
 * @param {number} shopId - Shop ID
 * @returns {Object} Order management methods
 */
const useOrderManagement = (rpc, shopId) => {
    /**
     * Calculate order counts by status
     * @param {Array} orders - List of orders
     * @param {number} shopId - Shop ID
     * @returns {Object} Counts by status
     */
    const calculateOrderCounts = (orders, shopId) => {
        const filterByStatus = (status) =>
            orders.filter(order =>
                order.order_status === status &&
                order.config_id[0] === shopId
            ).length;

        return {
            draft_count: filterByStatus(ORDER_STATUSES.DRAFT),
            waiting_count: filterByStatus(ORDER_STATUSES.WAITING),
            ready_count: filterByStatus(ORDER_STATUSES.READY)
        };
    };

    /**
     * Fetch order details from server
     * @returns {Promise<Object>} Order details and counts
     */
    const fetchOrderDetails = async () => {
        try {
            // const result = await orm.call("pos.order", "get_details", ["", shopId, ""]);

            const result = await rpc("/pos/kitchen/get_order_details", {
                shop_id: shopId
            });
            const rawLines = Array.isArray(result.order_lines) ? result.order_lines : [];
            const normalizedLines = rawLines.map((line) => {
                const isModifier = computeModifierFlag(line);
                const normalized = {
                    ...line,
                    sh_is_topping: normalizeBooleanFlag(line ? line.sh_is_topping : false),
                    is_topping: normalizeBooleanFlag(line ? line.is_topping : false),
                    is_modifier: isModifier,
                };
                console.debug('[Kitchen] normalized line', {
                    id: normalized.id,
                    product: normalized.full_product_name,
                    qty: normalized.qty,
                    raw_sh_is_topping: line ? line.sh_is_topping : undefined,
                    raw_is_topping: line ? line.is_topping : undefined,
                    normalized_sh_is_topping: normalized.sh_is_topping,
                    normalized_is_topping: normalized.is_topping,
                    is_modifier: normalized.is_modifier,
                });
                return normalized;
            });
            return {
                order_details: result.orders,
                lines: normalizedLines,
                ...calculateOrderCounts(result.orders, shopId)
            };
        } catch (error) {
            console.error("Error fetching order details:", error);
            return {
                order_details: [],
                lines: [],
                draft_count: 0,
                waiting_count: 0,
                ready_count: 0
            };
        }
    };

    return {
        fetchOrderDetails,
        calculateOrderCounts
    };
};

/**
 * Kitchen Dashboard Component
 */
export class KitchenScreenDashboard extends Component {
    /**
     * Component setup
     */
    setup() {
        this.initializeServices();
        this.initializeState();
        this.setupEventListeners();

        onWillUnmount(() => {
            if (this.refreshInterval) {
                clearInterval(this.refreshInterval);
            }
            this.busService.removeEventListener('notification', this.handleNotification);
        })
    }

    /**
     * Initialize required services
     */
    initializeServices() {
        this.busService = this.env.services.bus_service;
        this.orm = this.env.services.orm;
        this.rpc = this.env.services.rpc;
        this.user = this.env.services.user;
        this.notification = this.env.services.notification;
        // this.formatDateTime = formatDateTime;
    }

    /**
     * Initialize component state
     */
    initializeState() {
        const shopId = this.getShopId();

        this.state = useState({
            order_details: [],
            shop_id: shopId,
            stages: ORDER_STATUSES.DRAFT,
            draft_count: 0,
            waiting_count: 0,
            ready_count: 0,
            lines: [],
            loading: false,
            error: null,
            // Zoom UI state
            zoomIndex: 1,
            card_w: 360,
            card_h: 520,
            content_scale: 1,
        });

        this.orderManagement = useOrderManagement(this.rpc, shopId);
    }

    /**
     * Get shop ID from context or session storage
     * @returns {number} Shop ID
     */
    getShopId() {
        const contextShopId = odoo.shopId;
        if (contextShopId) {
            sessionStorage.setItem('shop_id', contextShopId);
            return contextShopId;
        }
        return parseInt(sessionStorage.getItem('shop_id'), 10);
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        this.busService.addChannel(BUS_CHANNEL);

        onWillStart(async () => {
            this.busService.addEventListener('notification', this.handleNotification.bind(this));
            await this.refreshOrderDetails();
            this.initZoomFromStorage();
        });

        onMounted(() => {
            this.startAutoRefresh();
        });
    }

    /**
     * Start auto-refresh timer
     */
    startAutoRefresh() {
        // Refresh every 5 seconds
        this.refreshInterval = setInterval(() => {
            this.refreshOrderDetails();
        }, 5000);
    }

    /**
     * Handle bus notifications
     * @param {Object} message - Notification message
     */
    async handleNotification(message) {
        const payload = message.detail[0].payload;
        if (payload.message === BUS_EVENT.MESSAGE &&
            payload.res_model === BUS_EVENT.MODEL) {
            await this.refreshOrderDetails();
        }
    }

    /**
     * Return true when a line represents a modifier/topping
     */
    isModifierLine(line) {
        if (!line) {
            return false;
        }
        if (typeof line.is_modifier === 'boolean') {
            console.debug('[Kitchen] using cached modifier flag', { id: line.id, product: line.full_product_name, is_modifier: line.is_modifier });
            return line.is_modifier;
        }
        const flag = computeModifierFlag(line);
        line.is_modifier = flag;
        line.sh_is_topping = normalizeBooleanFlag(line.sh_is_topping);
        line.is_topping = normalizeBooleanFlag(line.is_topping);
        console.debug('[Kitchen] computed modifier flag', { id: line.id, product: line.full_product_name, is_modifier: flag, sh_is_topping: line.sh_is_topping, is_topping: line.is_topping });
        return flag;
    }

    /**
     * Refresh order details
     */
    async refreshOrderDetails() {
        try {
            this.state.loading = true;
            this.state.error = null;
            const details = await this.orderManagement.fetchOrderDetails();
            Object.assign(this.state, details);
        } catch (error) {
            this.state.error = "Failed to refresh orders";
            this.notification.add("Failed to refresh orders", {
                title: "Error",
                type: "danger"
            });
        } finally {
            this.state.loading = false;
        }
    }

    /**
     * Update order status
     * @param {number} orderId - Order ID
     * @param {string} newStatus - New status
     * @param {string} methodName - Method to call
     */
    async updateOrderStatus(orderId, newStatus, methodName) {
        try {
            await this.rpc("/pos/kitchen/order_status", {
                method: methodName,
                order_id: Number(orderId),
            });

            const order = this.state.order_details.find(o => o.id === orderId);
            if (order) {
                order.order_status = newStatus;
                await this.refreshOrderDetails();
            }

            this.notification.add(`Order ${orderId} updated successfully`, {
                title: "Success",
                type: "success"
            });
        } catch (error) {
            console.error("Error updating order status:", error);
            this.notification.add(`Failed to update order ${orderId}`, {
                title: "Error",
                type: "danger"
            });
        }
    }

    get noOrders() {
        return _t("No orders !");
    }

    get orderInProgress() {
        return this.state.order_details.filter(o =>
            o.config_id[0] === this.state.shop_id &&
            o.order_status === 'draft')
    }

    get orderCompleted() {
        const userTimezone = this.user.tz || 'UTC';
        return this.state.order_details.filter(o => {
            // Ensure write_date is in a format Luxon can parse (e.g., "2024-11-12T09:00:46")
            const formattedWriteDate = o.write_date.replace(' ', 'T');

            // Parse the formatted date string in UTC and convert to user timezone
            const writeDate = DateTime.fromISO(formattedWriteDate, {zone: 'UTC'})
                .setZone(userTimezone);

            return (
                o.config_id[0] === this.state.shop_id &&
                o.order_status === 'ready' &&
                writeDate > DateTime.now().minus({minutes: 5})
            );
        });
    }

    // ===== Zoom controls =====
    initZoomFromStorage() {
        try {
            const stored = window.localStorage.getItem('kitchen_zoom_index');
            if (stored !== null) {
                this.state.zoomIndex = Number(stored);
            }
        } catch (_) { /* ignore */ }
        this.applyZoom();
    }

    zoomLevels() {
        // width, height, and content scale factor
        return [
            { w: 300, h: 460, s: 0.90 }, // compact
            { w: 360, h: 520, s: 1.00 }, // default
            { w: 420, h: 580, s: 1.10 }, // large
            { w: 500, h: 640, s: 1.20 }, // xlarge
        ];
    }

    applyZoom() {
        const levels = this.zoomLevels();
        const idx = Math.min(Math.max(this.state.zoomIndex, 0), levels.length - 1);
        const { w, h, s } = levels[idx];
        this.state.card_w = w;
        this.state.card_h = h;
        this.state.content_scale = s;
        try {
            window.localStorage.setItem('kitchen_zoom_index', String(idx));
        } catch (_) { /* ignore */ }
    }

    zoomIn() {
        this.state.zoomIndex = Math.min(this.state.zoomIndex + 1, this.zoomLevels().length - 1);
        this.applyZoom();
    }

    zoomOut() {
        this.state.zoomIndex = Math.max(this.state.zoomIndex - 1, 0);
        this.applyZoom();
    }

    zoomReset() {
        this.state.zoomIndex = 1; // default preset
        this.applyZoom();
    }


    // Cancel flow removed: Clover-style UX has no cancel popup

    /**
     * Complete order
     * @param {Integer} orderId - Integer object
     */
    async done_order(orderId) {
        await this.updateOrderStatus(
            orderId,
            ORDER_STATUSES.READY,
            "order_progress_change"
        );
    }

    /**
     * Toggle a line item readiness by id
     * @param {number} lineId
     */
    async accept_order_line(lineId) {
        try {
            const id = Number(lineId);
            const line = this.state.lines.find((l) => l.id === id);
            if (!line) return;
            // Do not toggle toppings/modifiers
            if (this.isModifierLine(line)) return;

            await this.orm.call("pos.order.line", "order_progress_change", [id]);

            // Local UI update
            line.order_status = line.order_status === ORDER_STATUSES.READY
                ? ORDER_STATUSES.WAITING
                : ORDER_STATUSES.READY;

            // If all main items are ready, mark the order as ready
            const order = this.getOrderByLineId(id);
            if (order && this.areAllMainItemsReady(order)) {
                await this.done_order(order.id);
            }

            this.notification.add("Item status updated", { title: "Success", type: "success" });
        } catch (error) {
            console.error("Error updating order line:", error);
            this.notification.add("Failed to update item", { title: "Error", type: "danger" });
        }
    }

    /**
     * Mark all main items in an order as ready and complete the order
     * @param {number} orderId
     */
    async mark_all_ready(orderId) {
        try {
            const id = Number(orderId);
            const order = this.state.order_details.find((o) => o.id === id);
            if (!order) return;

            const lineIds = Array.isArray(order.lines) ? order.lines : [];
            const lines = lineIds
                .map((lid) => this.state.lines.find((l) => l.id === lid))
                .filter(Boolean)
                .filter((l) => !this.isModifierLine(l))
                .filter((l) => l.order_status !== ORDER_STATUSES.READY);

            // Toggle only lines that are not yet ready
            for (const line of lines) {
                await this.orm.call("pos.order.line", "order_progress_change", [Number(line.id)]);
                line.order_status = ORDER_STATUSES.READY;
            }

            // Complete the order if all mains are now ready
            await this.done_order(id);
            await this.refreshOrderDetails();

            this.notification.add("Order marked as ready", { title: "Success", type: "success" });
        } catch (error) {
            console.error("Error marking all lines ready:", error);
            this.notification.add("Failed to mark all ready", { title: "Error", type: "danger" });
        }
    }

    /**
     * Find order containing given line id
     */
    getOrderByLineId(lineId) {
        return this.state.order_details.find((o) => Array.isArray(o.lines) && o.lines.includes(lineId)) || null;
    }

    /**
     * True if all non-modifier lines are ready for a given order
     */
    areAllMainItemsReady(order) {
        const ids = Array.isArray(order.lines) ? order.lines : [];
        const mains = ids
            .map((id) => this.state.lines.find((l) => l.id === id))
            .filter(Boolean)
            .filter((l) => !this.isModifierLine(l));
        return mains.length > 0 && mains.every((l) => l.order_status === ORDER_STATUSES.READY);
    }

    /**
     * Return line ids grouped by parent+modifiers with completed groups at the end
     */
    sortedLineIds(order) {
        const ids = Array.isArray(order.lines) ? order.lines.slice() : [];
        const getLine = (id) => this.state.lines.find((l) => l.id === id);
        const groups = [];
        let current = [];
        for (const id of ids) {
            const line = getLine(id);
            if (!line) continue;
            const isModifier = this.isModifierLine(line);
            console.debug('[Kitchen] sortedLineIds classification', { id, product: line.full_product_name, is_modifier: isModifier });
            if (!isModifier) {
                if (current.length) groups.push(current);
                current = [id];
            } else {
                if (current.length) current.push(id);
                else current = [id];
            }
        }
        if (current.length) groups.push(current);

        const isGroupReady = (g) => {
            const parent = getLine(g[0]);
            return parent && parent.order_status === ORDER_STATUSES.READY;
        };

        const pending = [];
        const completed = [];
        for (const g of groups) {
            (isGroupReady(g) ? completed : pending).push(g);
        }
        return pending.concat(completed).flat();
    }
    // Removed auto-completion and custom sorting; using original order

    /**
     * Group line ids into [parent, ...modifiers] sequences
     */
    

    /**
     * Return a mixed sequence of entries for template rendering:
     * - { t: 'line', id }
     * - { t: 'divider' } inserted between pending and completed groups
     */
    linesWithDivider(order) {
        const ids = Array.isArray(order.lines) ? order.lines.slice() : [];
        const getLine = (id) => this.state.lines.find((l) => l.id === id);

        // Build groups: [parent, ...modifiers]
        const groups = [];
        let current = [];
        for (const id of ids) {
            const line = getLine(id);
            if (!line) continue;
            const isModifier = this.isModifierLine(line);
            console.debug('[Kitchen] linesWithDivider classification', { id, product: line.full_product_name, is_modifier: isModifier });
            if (!isModifier) {
                if (current.length) groups.push(current);
                current = [id];
            } else {
                if (current.length) current.push(id);
                else current = [id];
            }
        }
        if (current.length) groups.push(current);

        const isGroupReady = (g) => {
            const parent = getLine(g[0]);
            return parent && parent.order_status === ORDER_STATUSES.READY;
        };

        const pending = [];
        const completed = [];
        for (const g of groups) {
            (isGroupReady(g) ? completed : pending).push(g);
        }

        const out = [];
        for (const g of pending) for (const id of g) out.push({ t: 'line', id });
        if (pending.length && completed.length) out.push({ t: 'divider' });
        for (const g of completed) for (const id of g) out.push({ t: 'line', id });
        return out;
    }

    /**
     * Set current stage
     * @param {string} stage - Stage to set
     */
    setStage(stage) {
        this.state.stages = stage;
    }

    /**
     * Set ready stage
     */
    ready_stage() {
        this.setStage(ORDER_STATUSES.READY);
    }

    /**
     * Set waiting stage
     */
    waiting_stage() {
        this.setStage(ORDER_STATUSES.WAITING);
    }

    /**
     * Set draft stage
     */
    draft_stage() {
        this.setStage(ORDER_STATUSES.DRAFT);
    }

}

// Component registration
KitchenScreenDashboard.template = 'KitchenCustomDashBoard';
registry.category("actions").add("kitchen_custom_dashboard_tags", KitchenScreenDashboard);


export async function createKitchenApp() {
    await whenReady();
    const appEnv = makeEnv();
    await startServices(appEnv);
    const app = new App(KitchenScreenDashboard, {
        templates,
        env: appEnv,
        dev: appEnv.debug,
        translateFn: _t,
        translatableAttributes: ["data-tooltip"],
    });
    return app.mount(document.body);
}

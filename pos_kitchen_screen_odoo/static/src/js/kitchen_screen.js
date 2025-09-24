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

// Feature flag: disable all localStorage-based delta caching (seen lines/tickets/press counts/virtual lines)
const DISABLE_LOCAL_CACHE = true;
// Debug toggle: enable via ?kdebug=1 or localStorage 'kitchen_debug' = '1'|'true'
const isDebugEnabled = () => {
    try {
        const params = new URLSearchParams(window.location.search);
        const q = params.get('kdebug');
        if (q !== null) return q !== '0' && q.toLowerCase() !== 'false';
    } catch (_) { /* ignore */ }
    try {
        const v = String(window.localStorage.getItem('kitchen_debug') || '').toLowerCase();
        return v === '1' || v === 'true' || v === 'yes';
    } catch (_) { /* ignore */ }
    return Boolean((window.odoo && window.odoo.debug) || false);
};
const __KITCHEN_DEBUG__ = isDebugEnabled();

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

const extractToppingFlags = (line, product) => {
    const lineFlagRaw = line && (line.is_topping ?? line.sh_is_topping);
    const productFlagRaw = product && (product.is_topping ?? product.sh_is_topping);
    const denormFlagRaw = line && (line.product_is_topping ?? line.product_sh_is_topping);
    const hasFlag = normalizeBooleanFlag(line && (line.sh_is_has_topping ?? line.is_has_topping));

    const productFlag = normalizeBooleanFlag(productFlagRaw) || normalizeBooleanFlag(denormFlagRaw);
    const lineFlag = normalizeBooleanFlag(lineFlagRaw) || productFlag;

    return {
        is_topping: lineFlag,
        sh_is_topping: lineFlag,
        sh_is_has_topping: hasFlag,
        product_is_topping: productFlag,
        product_sh_is_topping: productFlag,
    };
};

const computeModifierFlag = (line, product) => {
    if (!line) {
        return false;
    }
    const flags = extractToppingFlags(line, product);
    return flags.is_topping;
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

const storageKeyForLines = (sid) => `kitchen_seen_lines_${sid}`;
const storageKeyForTickets = (sid) => `kitchen_seen_tickets_${sid}`;
const storageKeyForPressCounts = (sid) => `kitchen_press_counts_${sid}`;

const loadSeenLines = (sid) => {
    try {
        const raw = window.localStorage.getItem(storageKeyForLines(sid));
        return raw ? JSON.parse(raw) : {};
    } catch (_) { return {}; }
};

const saveSeenLines = (sid, data) => {
    try { window.localStorage.setItem(storageKeyForLines(sid), JSON.stringify(data)); } catch (_) { /* ignore */ }
};

const loadSeenTickets = (sid) => {
    try {
        const raw = window.localStorage.getItem(storageKeyForTickets(sid));
        const parsed = raw ? JSON.parse(raw) : null;
        // Backward compatibility: previously we stored an array or order-id map.
        // Convert to a generic map keyed by a ticket key (orderId_pressIndex) or fallback to orderId.
        if (Array.isArray(parsed)) {
            const map = {};
            for (const t of parsed) {
                if (t && typeof t.id === 'number') map[`${t.id}_1`] = t;
            }
            return map;
        }
        return parsed && typeof parsed === 'object' ? parsed : {};
    } catch (_) { return {}; }
};

const saveSeenTickets = (sid, ticketsByOrderId) => {
    try { window.localStorage.setItem(storageKeyForTickets(sid), JSON.stringify(ticketsByOrderId)); } catch (_) { /* ignore */ }
};

const loadPressCounts = (sid) => {
    try {
        const raw = window.localStorage.getItem(storageKeyForPressCounts(sid));
        const obj = raw ? JSON.parse(raw) : {};
        return obj && typeof obj === 'object' ? obj : {};
    } catch (_) { return {}; }
};

const savePressCounts = (sid, obj) => {
    try { window.localStorage.setItem(storageKeyForPressCounts(sid), JSON.stringify(obj)); } catch (_) { /* ignore */ }
};

let __deltaVirtualId = -1;

const computeDeltaTickets = (orders, allLines, sid) => {
    const seenLines = loadSeenLines(sid);
    const ticketsByKey = loadSeenTickets(sid);   // map: ticketKey -> ticket
    const pressCounts = loadPressCounts(sid);    // map: orderId -> last press index

    const byOrder = new Map();
    for (const line of allLines || []) {
        if (!line || !Array.isArray(line.order_id)) continue;
        const orderId = line.order_id[0];
        if (!byOrder.has(orderId)) byOrder.set(orderId, []);
        byOrder.get(orderId).push(line);
    }

    const virtualLines = [];
    for (const order of orders || []) {
        const orderId = order.id;
        const lines = byOrder.get(orderId) || [];
        const prev = seenLines[orderId] || {};

        // Build current snapshot map id -> qty
        const cur = {};
        for (const l of lines) {
            cur[l.id] = Number(l.qty) || 0;
        }

        // Determine delta additions
        const deltaIds = [];
        for (const l of lines) {
            const prevQty = Number(prev[l.id] || 0);
            const curQty = Number(cur[l.id] || 0);
            if (curQty > prevQty) {
                deltaIds.push({ id: l.id, add: curQty - prevQty });
            }
        }

        // First time we see this order: create initial ticket with all lines
        const isFirstSeen = !seenLines.hasOwnProperty(orderId);
        let ticketLines = [];
        let makeTicket = false;
        if (isFirstSeen && lines.length) {
            pressCounts[orderId] = 1;
            ticketLines = lines.map((l) => l.id);
            makeTicket = true;
        } else if (deltaIds.length) {
            const curPress = Number(pressCounts[orderId] || 0) + 1;
            pressCounts[orderId] = curPress;
            ticketLines = deltaIds.map((x) => x.id);
            makeTicket = true;
        }

        if (makeTicket && ticketLines.length) {
            // Remove any existing badges for this order so only the new badge remains
            for (const key of Object.keys(ticketsByKey)) {
                // keys are `${orderId}_pressIndex`, keep only those not matching this order
                if (String(key).startsWith(`${orderId}_`)) {
                    delete ticketsByKey[key];
                }
            }
            // Create virtual line snapshot records so old badges never go empty
            const byId = new Map(lines.map((l) => [l.id, l]));
            const deltaMap = new Map();
            for (const d of deltaIds) deltaMap.set(d.id, d.add);
            const vIds = [];
            for (const baseId of ticketLines) {
                const base = byId.get(baseId) || allLines.find((l) => l.id === baseId);
                const qty = deltaMap.has(baseId) ? Number(deltaMap.get(baseId)) || 0 : Number(base && base.qty) || 0;
                if (!base || qty <= 0) continue;
                const v = {
                    id: __deltaVirtualId--,
                    full_product_name: base.full_product_name || base.product || base.display_name || 'Item',
                    qty: qty,
                    order_status: base.order_status || 'waiting',
                    is_modifier: false,
                    is_topping: false,
                    sh_is_topping: false,
                    product_is_topping: false,
                    product_sh_is_topping: false,
                    sh_is_has_topping: false,
                };
                virtualLines.push(v);
                vIds.push(v.id);
            }

            const key = `${orderId}_${pressCounts[orderId]}`;
            ticketsByKey[key] = {
                ...order,
                ticket_uid: `order-${orderId}-press-${pressCounts[orderId]}`,
                ticket_created_at: order.write_date,
                lines: vIds,
            };
        }

        // Persist snapshot
        seenLines[orderId] = cur;
    }

    saveSeenLines(sid, seenLines);
    saveSeenTickets(sid, ticketsByKey);
    savePressCounts(sid, pressCounts);
    // Render only non-empty tickets to avoid blank cards
    const tickets = Object.values(ticketsByKey).filter((t) => Array.isArray(t.lines) && t.lines.length);
    return { tickets, virtualLines };
};

const fetchOrderDetails = async () => {
    try {
        const result = await rpc("/pos/kitchen/get_order_details", {
            shop_id: shopId
        });

        if (result && result.error === "no_open_session") {
            return {
                order_details: [],
                tickets: [],
                lines: [],
                draft_count: 0,
                waiting_count: 0,
                ready_count: 0,
                session_error: true,
            };
        }

        const rawOrders = Array.isArray(result?.orders) ? result.orders : [];
        const normalizedOrders = rawOrders.map((order) => {
            const summaryRaw = Array.isArray(order.kitchen_new_line_summary) ? order.kitchen_new_line_summary : [];
            const sanitizedSummary = summaryRaw.map((entry) => ({
                product_id: entry && entry.product_id,
                product_name: (entry && (entry.product_name || entry.name)) || '',
                quantity: Number(entry && entry.quantity) || 0,
                note: entry && entry.note ? entry.note : '',
                ticket_uid: entry && entry.ticket_uid,
            }));
            let explicitCount = 0;
            if (typeof order.kitchen_new_line_count === 'number') {
                explicitCount = order.kitchen_new_line_count;
            } else {
                explicitCount = sanitizedSummary.reduce((acc, entry) => {
                    const numeric = Number(entry.quantity) || 0;
                    return acc + (numeric > 0 ? numeric : 0);
                }, 0);
            }
            const normalizedCount = Math.round(explicitCount * 100) / 100;
            return {
                ...order,
                kitchen_new_line_summary: sanitizedSummary,
                kitchen_new_line_count: normalizedCount,
            };
        });

        // Normalize lines before building tickets
        const rawLines = Array.isArray(result?.order_lines) ? result.order_lines : [];
        let normalizedLines = rawLines.map((line) => {
            const flags = extractToppingFlags(line, null);
            const isModifier = flags.is_topping;
            const normalized = {
                ...line,
                is_topping: flags.is_topping,
                sh_is_topping: flags.sh_is_topping,
                product_is_topping: flags.product_is_topping,
                product_sh_is_topping: flags.product_sh_is_topping,
                sh_is_has_topping: flags.sh_is_has_topping,
                is_modifier: isModifier,
            };
            if (__KITCHEN_DEBUG__) console.debug('[Kitchen] normalized line', {
                id: normalized.id,
                product: normalized.full_product_name,
                qty: normalized.qty,
                raw_line_is_topping: line ? line.is_topping : undefined,
                raw_sh_is_topping: line ? line.sh_is_topping : undefined,
                raw_product_is_topping: line ? line.product_is_topping : undefined,
                raw_product_sh_is_topping: line ? line.product_sh_is_topping : undefined,
                raw_sh_is_has_topping: line ? line.sh_is_has_topping : undefined,
                normalized_is_topping: normalized.is_topping,
                normalized_product_is_topping: normalized.product_is_topping,
                normalized_sh_is_has_topping: normalized.sh_is_has_topping,
                is_modifier: normalized.is_modifier,
            });
            return normalized;
        });

          // Prefer server-provided logs if present; otherwise build full tickets (no local delta caching)
          let tickets = [];
          const anyLogs = normalizedOrders.some((o) => Array.isArray(o.kitchen_send_logs) && o.kitchen_send_logs.length);
          if (anyLogs) {
              // Build exactly one badge per order. If the order has logs, use the latest delta;
              // otherwise, fall back to all current order lines so it still renders.
            for (const order of normalizedOrders) {
                const logs = Array.isArray(order.kitchen_send_logs) ? order.kitchen_send_logs : [];
                if (!logs.length) {
                    const allIds = Array.isArray(order.lines) ? order.lines.map((x) => Number(x)) : [];
                    if (allIds.length) {
                        tickets.push({
                            ...order,
                            ticket_uid: `order-${order.id}-full`,
                            ticket_created_at: order.write_date,
                            lines: allIds,
                        });
                    }
                    continue;
                }

                // Sort logs in ascending time so we can diff cumulatively.
                const sorted = logs.slice().sort((a, b) => {
                    const sa = String(a.created_at || '').replace(' ', 'T');
                    const sb = String(b.created_at || '').replace(' ', 'T');
                    const da = DateTime.fromISO(sa, { zone: 'UTC' });
                    const db = DateTime.fromISO(sb, { zone: 'UTC' });
                    if (!da.isValid && !db.isValid) return 0;
                    if (!da.isValid) return -1;
                    if (!db.isValid) return 1;
                    return da - db;
                });

                const seenIds = new Set();
                let lastDeltaIds = [];
                let lastCreatedAt = order.write_date;
                let lastIds = [];
                for (const log of sorted) {
                    const ids = Array.isArray(log.line_ids) ? log.line_ids.map((lid) => Number(lid)) : [];
                    const delta = ids.filter((id) => !seenIds.has(id));
                    ids.forEach((id) => seenIds.add(id));
                    lastDeltaIds = delta;
                    lastIds = ids;
                    lastCreatedAt = log.created_at || order.write_date;
                }

                // Create one badge per order. Prefer the latest delta; if empty, fall back to
                // the latest log's ids; if still empty, fall back to all order lines.
                let linesForTicket = lastDeltaIds;
                if (!linesForTicket || !linesForTicket.length) {
                    linesForTicket = Array.isArray(lastIds) && lastIds.length
                        ? lastIds
                        : (Array.isArray(order.lines) ? order.lines.map((lid) => Number(lid)) : []);
                }
                tickets.push({
                    ...order,
                    ticket_uid: `ticket-${order.id}-latest`,
                    ticket_created_at: lastCreatedAt,
                    lines: linesForTicket,
                });
            }

            // Filter out empty tickets (safety)
            tickets = tickets.filter((t) => Array.isArray(t.lines) && t.lines.length);
        } else {
            // Build one ticket per order using all current order lines (no delta/local cache)
            tickets = (normalizedOrders || []).map((order) => ({
                ...order,
                ticket_uid: `order-${order.id}-full`,
                ticket_created_at: order.write_date,
                lines: Array.isArray(order.lines) ? order.lines.map((lid) => Number(lid)) : [],
            })).filter((t) => Array.isArray(t.lines) && t.lines.length);
        }
        return {
            order_details: normalizedOrders,
            tickets,
            lines: normalizedLines,
            draft_count: 0,
            waiting_count: 0,
            ready_count: 0,
            session_error: false,
        };
    } catch (error) {
        console.error("Error fetching order details:", error);
        return {
            order_details: [],
            tickets: [],
            lines: [],
            draft_count: 0,
            waiting_count: 0,
            ready_count: 0,
            session_error: false,
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
            tickets: [],
            shop_id: shopId,
            stages: ORDER_STATUSES.DRAFT,
            draft_count: 0,
            waiting_count: 0,
            ready_count: 0,
            lines: [],
            loading: false,
            error: null,
            session_error: false,
            // Zoom UI state
            zoomIndex: 2,
            card_w: 320,
            card_h: 400,
            content_scale: 1,
            // Completed window (minutes); 0 = show all
            completed_window_minutes: 5,
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
            if (!DISABLE_LOCAL_CACHE) this.checkBootTokenAndReset();
            await this.refreshOrderDetails();
            this.initZoomFromStorage();
            this.loadCompletedWindow();
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

    // Clear per-shop caches on first load when server boot token changes
    checkBootTokenAndReset() {
        try {
            const sid = this.state?.shop_id || sessionStorage.getItem('shop_id');
            if (!sid) return;
            const boot = (window.odoo && (window.odoo.kitchen_boot_ts || (window.odoo.session_info && window.odoo.session_info.kitchen_boot_ts))) || null;
            if (!boot) return;
            const key = `kitchen_boot_ts_${sid}`;
            const prev = window.localStorage.getItem(key);
            if (prev !== String(boot)) {
                const keys = [
                    `kitchen_seen_lines_${sid}`,
                    `kitchen_seen_tickets_${sid}`,
                    `kitchen_press_counts_${sid}`,
                    `kitchen_virtual_lines_${sid}`,
                ];
                for (const k of keys) { try { window.localStorage.removeItem(k); } catch (_) { /* ignore */ } }
                try { window.localStorage.setItem(key, String(boot)); } catch (_) { /* ignore */ }
            }
        } catch (_) { /* ignore */ }
    }

    // ===== Completed window controls =====
    completedWindowKey() {
        const sid = this.state.shop_id || sessionStorage.getItem('shop_id');
        return `kitchen_completed_window_minutes_${sid || 'global'}`;
    }
    loadCompletedWindow() {
        try {
            const raw = window.localStorage.getItem(this.completedWindowKey());
            const n = Number(raw);
            if (!Number.isNaN(n)) this.state.completed_window_minutes = n;
        } catch (_) { /* ignore */ }
    }
    saveCompletedWindow() {
        try { window.localStorage.setItem(this.completedWindowKey(), String(this.state.completed_window_minutes)); } catch (_) { /* ignore */ }
    }
    onChangeCompletedWindow(value) {
        const n = Number(value);
        this.state.completed_window_minutes = Number.isNaN(n) ? 0 : n;
        this.saveCompletedWindow();
    }

    /**
     * Reset local, per-shop kitchen UI state persisted in localStorage
     * Clears: seen lines, seen tickets, press counts, and virtual lines
     */
    resetKitchenState() {
        try {
            const sid = this.state.shop_id || sessionStorage.getItem('shop_id');
            if (!sid) return;
            // Keys maintained by this screen for deltas/badges
            // Build keys inline (helpers live in a different scope)
            const keys = [
                `kitchen_seen_lines_${sid}`,
                `kitchen_seen_tickets_${sid}`,
                `kitchen_press_counts_${sid}`,
                `kitchen_virtual_lines_${sid}`,
            ];
            for (const k of keys) {
                try { window.localStorage.removeItem(k); } catch (_) { /* ignore */ }
            }
            // Soft reset UI bits that depend on those caches
            this.state.tickets = [];
            // Remove any negative-id virtual lines from memory
            this.state.lines = (this.state.lines || []).filter((l) => !(typeof l?.id === 'number' && l.id < 0));
            this.recomputeTicketCounts();
            this.notification.add(_t('Kitchen state cleared'), { title: _t('Kitchen Screen'), type: 'success' });
            // Reload fresh data
            this.refreshOrderDetails();
        } catch (e) {
            console.error('Failed to reset kitchen state', e);
            this.notification.add(_t('Failed to clear kitchen state'), { title: _t('Kitchen Screen'), type: 'danger' });
        }
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
            if (__KITCHEN_DEBUG__) console.debug('[Kitchen] using cached modifier flag', { id: line.id, product: line.full_product_name, is_modifier: line.is_modifier });
            return line.is_modifier;
        }
        const flags = extractToppingFlags(line, null);
        const flag = flags.is_topping;
        line.is_modifier = flag;
        line.is_topping = flags.is_topping;
        line.sh_is_topping = flags.sh_is_topping;
        line.product_is_topping = flags.product_is_topping;
        line.product_sh_is_topping = flags.product_sh_is_topping;
        line.sh_is_has_topping = flags.sh_is_has_topping;
        if (__KITCHEN_DEBUG__) console.debug('[Kitchen] computed modifier flag', { id: line.id, product: line.full_product_name, is_modifier: flag, is_topping: line.is_topping, product_is_topping: line.product_is_topping });
        return flag;
    }

    /**
     * Refresh order details
     */
    async refreshOrderDetails() {
        try {
            this.state.loading = true;
            this.state.error = null;
            const previousSessionError = this.state.session_error;
            const details = await this.orderManagement.fetchOrderDetails();
            Object.assign(this.state, details);
            // Skip persisted virtual lines when local cache is disabled
            if (!DISABLE_LOCAL_CACHE) {
                try {
                    const sid = this.state.shop_id || sessionStorage.getItem('shop_id');
                    const persisted = window.localStorage.getItem(`kitchen_virtual_lines_${sid}`);
                    const arr = persisted ? JSON.parse(persisted) : [];
                    if (Array.isArray(arr) && arr.length) {
                        this.state.lines = (this.state.lines || []).concat(arr);
                    }
                    const currentVirtual = (this.state.lines || []).filter((l) => typeof l?.id === 'number' && l.id < 0);
                    const byId = new Map((Array.isArray(arr) ? arr : []).map((v) => [v.id, v]));
                    for (const v of currentVirtual) {
                        if (!byId.has(v.id)) byId.set(v.id, v);
                    }
                    const merged = Array.from(byId.values());
                    window.localStorage.setItem(`kitchen_virtual_lines_${sid}`, JSON.stringify(merged));
                } catch (_) { /* ignore */ }
            }
            // tickets computed in fetchOrderDetails, no need to rebuild
            this.recomputeTicketCounts();
            this.recomputeTicketCounts();

            if (this.state.session_error && !previousSessionError) {
                this.notification.add(_t("No open POS session found. Please start a session to display kitchen orders."), {
                    title: _t("Kitchen Screen"),
                    type: "warning",
                });
            }
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
        return this.ticketsInProgress;
    }

    get orderCompleted() {
        return this.ticketsCompleted;
    }

    newLineSummary(order) {
        if (!order) {
            return [];
        }
        const summary = order.kitchen_new_line_summary;
        return Array.isArray(summary) ? summary : [];
    }

    newLineCount(order) {
        if (!order) {
            return 0;
        }
        if (typeof order.kitchen_new_line_count === 'number') {
            return Math.round(order.kitchen_new_line_count * 100) / 100;
        }
        const total = this.newLineSummary(order).reduce((acc, entry) => {
            const quantity = entry && entry.quantity;
            const numeric = Number(quantity) || 0;
            return acc + (numeric > 0 ? numeric : 0);
        }, 0);
        return Math.round(total * 100) / 100;
    }

    formatNewLineQuantity(quantity) {
        const numeric = Number(quantity) || 0;
        return Math.round(numeric * 100) / 100;
    }


    buildTickets(orders, allLines) {
        const tickets = [];
        const getLine = (id) => (allLines || []).find((l) => l.id === Number(id));
        for (const order of orders || []) {
            const logs = Array.isArray(order.kitchen_send_logs) ? order.kitchen_send_logs : [];
            if (!logs.length) {
                const orderLineIds = Array.isArray(order.lines) ? order.lines.slice() : [];
                tickets.push({
                    ...order,
                    ticket_uid: `order-${order.id}`,
                    ticket_created_at: order.write_date,
                    lines: orderLineIds,
                });
                continue;
            }
            logs.forEach((log, index) => {
                const ids = Array.isArray(log.line_ids) ? log.line_ids.map((x) => Number(x)) : [];
                tickets.push({
                    ...order,
                    ticket_uid: log.ticket_uid || `ticket-${order.id}-${index}`,
                    ticket_created_at: log.created_at || order.write_date,
                    lines: ids,
                });
            });
        }
        return tickets;
    }


ticketLineRecords(ticket) {
    const lineIds = Array.isArray(ticket && ticket.lines) ? ticket.lines : [];
    return lineIds
        .map((id) => this.state.lines.find((line) => line.id === id))
        .filter(Boolean);
}

ticketStatus(ticket) {
    if (!ticket) {
        return ORDER_STATUSES.DRAFT;
    }
    // If the server already marks the order as ready, trust it
    if (ticket.order_status === ORDER_STATUSES.READY) {
        return ORDER_STATUSES.READY;
    }
    const records = this.ticketLineRecords(ticket);
    if (!records.length) {
        return ticket.order_status || ORDER_STATUSES.DRAFT;
    }
    const mains = records.filter((line) => !this.isModifierLine(line));
    if (!mains.length) {
        return ORDER_STATUSES.READY;
    }
    const hasWaiting = mains.some((line) => line.order_status === ORDER_STATUSES.WAITING);
    const allReady = mains.every((line) => line.order_status === ORDER_STATUSES.READY);
    if (allReady) {
        return ORDER_STATUSES.READY;
    }
    if (hasWaiting) {
        return ORDER_STATUSES.WAITING;
    }
    return ORDER_STATUSES.DRAFT;
}

ticketCreatedAt(ticket) {
    const source = ticket && (ticket.ticket_created_at || ticket.write_date || ticket.date_order);
    if (!source) {
        return DateTime.now();
    }
    const formatted = String(source).replace(' ', 'T');
    return DateTime.fromISO(formatted, { zone: 'UTC' });
}

get ticketsInProgress() {
    return (this.state.tickets || [])
        .filter((ticket) => {
            const status = this.ticketStatus(ticket);
            return status === ORDER_STATUSES.DRAFT || status === ORDER_STATUSES.WAITING;
        })
        .sort((a, b) => this.ticketCreatedAt(a) - this.ticketCreatedAt(b));
}

get ticketsCompleted() {
    const minutes = Number(this.state.completed_window_minutes) || 0;
    const list = (this.state.tickets || []).filter((t) => this.ticketStatus(t) === ORDER_STATUSES.READY);
    if (minutes <= 0) {
        return list.sort((a, b) => this.ticketCreatedAt(b) - this.ticketCreatedAt(a));
    }
    const userTimezone = this.user.tz || 'UTC';
    const cutoff = DateTime.now().setZone(userTimezone).minus({ minutes });
    return list
        .filter((ticket) => this.ticketCreatedAt(ticket).setZone(userTimezone) > cutoff)
        .sort((a, b) => this.ticketCreatedAt(b) - this.ticketCreatedAt(a));
}

recomputeTicketCounts() {
    let draft = 0;
    let waiting = 0;
    let ready = 0;
    for (const ticket of this.state.tickets || []) {
        const status = this.ticketStatus(ticket);
        if (status === ORDER_STATUSES.READY) {
            ready += 1;
        } else if (status === ORDER_STATUSES.WAITING) {
            waiting += 1;
        } else {
            draft += 1;
        }
    }
    this.state.draft_count = draft;
    this.state.waiting_count = waiting;
    this.state.ready_count = ready;
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
        // width changes with zoom; height is fixed to 400; no inner scaling
        return [
            { w: 260, h: 400, s: 1.00 }, // xs
            { w: 300, h: 400, s: 1.00 }, // compact
            { w: 320, h: 400, s: 1.00 }, // default (new)
            { w: 380, h: 400, s: 1.00 }, // large
            { w: 440, h: 400, s: 1.00 }, // xlarge
        ];
    }

    applyZoom() {
        const levels = this.zoomLevels();
        const idx = Math.min(Math.max(this.state.zoomIndex, 0), levels.length - 1);
        const { w, h, s } = levels[idx];
        this.state.card_w = w;
        this.state.card_h = h; // fixed to 400 via levels
        this.state.content_scale = s; // 1.00 (no scaling)
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
        this.state.zoomIndex = 2; // default preset (matches 320px)
        this.applyZoom();
    }


    // Cancel flow removed: Clover-style UX has no cancel popup

    /**
     * Complete order
     * @param {Integer} orderId - Integer object
     */
    async done_order(orderId) {
        try {
            const id = Number(orderId);
            const order = this.state.order_details.find((o) => o.id === id);
            if (!order) {
                // Fallback: still request recompute
                await this.updateOrderStatus(id, ORDER_STATUSES.READY, "order_progress_change");
                return;
            }
            // Collect all non-ready, non-modifier main lines
            const ids = Array.isArray(order.lines) ? order.lines.map((x) => Number(x)) : [];
            const targetLines = ids
                .map((lid) => this.state.lines.find((l) => l.id === lid))
                .filter(Boolean)
                .filter((l) => !this.isModifierLine(l))
                .filter((l) => l.order_status !== ORDER_STATUSES.READY);

            if (targetLines.length) {
                const nonReadyIds = targetLines
                    .map((l) => Number(l.id))
                    .filter((n) => Number.isFinite(n) && n > 0);
                if (nonReadyIds.length) {
                    await this.rpc("/pos/kitchen/line_status", { line_ids: nonReadyIds });
                    // Optimistic UI update
                    for (const l of targetLines) l.order_status = ORDER_STATUSES.READY;
                }
            }

            // Now recompute on the backend; this will set the order to ready
            await this.updateOrderStatus(id, ORDER_STATUSES.READY, "order_progress_change");
        } catch (e) {
            console.error("Failed to complete order:", e);
            this.notification.add("Failed to complete order", { title: "Error", type: "danger" });
        }
    }

    /**
     * Toggle a line item readiness by id
     * @param {number} lineId
     */
    async accept_order_line(lineId) {
        try {
            const id = Number(lineId);
            if (!Number.isFinite(id) || id <= 0) return;
            const line = this.state.lines.find((l) => l.id === id);
            if (!line) return;
            // Do not toggle toppings/modifiers
            if (this.isModifierLine(line)) return;

            // Use backend endpoint with sudo to avoid ACL issues on public sessions
            await this.rpc("/pos/kitchen/line_status", { line_ids: [id] });

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
    async mark_all_ready(orderId, ticketLineIds = null) {
        try {
            const id = Number(orderId);
            const order = this.state.order_details.find((o) => o.id === id);
            if (!order) return;

            const targetLineIds = Array.isArray(ticketLineIds) && ticketLineIds.length
                ? ticketLineIds.map((lid) => Number(lid))
                : (Array.isArray(order.lines) ? order.lines.map((lid) => Number(lid)) : []);

            const targetLines = targetLineIds
                .map((lid) => this.state.lines.find((l) => l.id === lid))
                .filter(Boolean)
                .filter((l) => !this.isModifierLine(l))
                .filter((l) => l.order_status !== ORDER_STATUSES.READY);

            if (targetLines.length) {
                const idsToToggle = targetLines.map((line) => Number(line.id));
                // Use backend endpoint with sudo to avoid ACL issues on public sessions
                await this.rpc("/pos/kitchen/line_status", { line_ids: idsToToggle });
                for (const line of targetLines) {
                    line.order_status = ORDER_STATUSES.READY;
                }
            }

            if (this.areAllMainItemsReady(order)) {
                await this.done_order(id);
            } else {
                await this.refreshOrderDetails();
            }

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
            if (__KITCHEN_DEBUG__) console.debug('[Kitchen] sortedLineIds classification', { id, product: line.full_product_name, is_modifier: isModifier });
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
            if (__KITCHEN_DEBUG__) console.debug('[Kitchen] linesWithDivider classification', { id, product: line.full_product_name, is_modifier: isModifier });
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

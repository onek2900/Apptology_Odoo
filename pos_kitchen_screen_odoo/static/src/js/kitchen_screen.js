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

// Client-side local delta caching removed; server summaries are the source of truth.
// Support live delta pushes via bus ('kitchen.delta') for immediate rendering.
// Persist only live tickets/lines in localStorage so they survive page reloads.
let __deltaVirtualId = -1;

const liveTicketsKey = (sid) => `kitchen_live_tickets_${sid}`;
const liveLinesKey = (sid) => `kitchen_live_lines_${sid}`;
const pressCountsKey = (sid) => `kitchen_press_counts_${sid}`;
const loadLiveState = (sid) => {
    try {
        const tRaw = window.localStorage.getItem(liveTicketsKey(sid));
        const lRaw = window.localStorage.getItem(liveLinesKey(sid));
        const tickets = tRaw ? JSON.parse(tRaw) : [];
        const lines = lRaw ? JSON.parse(lRaw) : [];
        return {
            tickets: Array.isArray(tickets) ? tickets : [],
            lines: Array.isArray(lines) ? lines : [],
        };
    } catch (_) { return { tickets: [], lines: [] }; }
};
const saveLiveState = (sid, tickets, lines) => {
    try {
        window.localStorage.setItem(liveTicketsKey(sid), JSON.stringify(tickets || []));
        window.localStorage.setItem(liveLinesKey(sid), JSON.stringify(lines || []));
    } catch (_) { /* ignore */ }
};
const loadPressCounts = (sid) => { try { const raw = window.localStorage.getItem(pressCountsKey(sid)); const obj = raw ? JSON.parse(raw) : {}; return obj && typeof obj === 'object' ? obj : {}; } catch (_) { return {}; } };
const savePressCounts = (sid, obj) => { try { window.localStorage.setItem(pressCountsKey(sid), JSON.stringify(obj || {})); } catch (_) { /* ignore */ } };
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

// Client-side local delta caching removed.

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

            // Prefer explicit per-press tickets from server if present
            const rawTickets = Array.isArray(result?.tickets) ? result.tickets : [];
            let tickets = [];
            if (rawTickets.length) {
                const byId = new Map((normalizedOrders || []).map((o) => [o.id, o]));
                tickets = rawTickets.map((t) => {
                    const oid = Array.isArray(t.order_id) ? Number(t.order_id[0]) : Number(t.order_id);
                    const order = byId.get(oid) || {};
                    return {
                        ...order,
                        ticket_uid: t.ticket_uid || `ticket-${oid}-${t.press_index}`,
                        ticket_created_at: t.created_at || order.write_date,
                        lines: Array.isArray(t.line_ids) ? t.line_ids.map((n) => Number(n)) : [],
                        kitchen_press_index: typeof t.press_index === 'number' ? t.press_index : undefined,
                        ticket_state: t.state || 'inprogress',
                    };
                }).filter((tk) => Array.isArray(tk.lines) && tk.lines.length);
            } else {
                // Fallback: one ticket per order using current lines
                tickets = (normalizedOrders || [])
                    .map((order) => ({
                        ...order,
                        ticket_uid: `order-${order.id}-full`,
                        ticket_created_at: order.write_date,
                        lines: Array.isArray(order.lines) ? order.lines.map((lid) => Number(lid)) : [],
                    }))
                    .filter((t) => Array.isArray(t.lines) && t.lines.length);
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
            // no periodic refresh to clear
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
            // Default height follows the zoom preset at index 2
            // Mapping of widths/heights handled in zoomLevels()
            card_h: 520,
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
        try { this.busService.addChannel('kitchen.delta'); } catch (_) { /* ignore */ }
        try { this.busService.addChannel('kitchen.session'); } catch (_) { /* ignore */ }

        onWillStart(async () => {
            this.busService.addEventListener('notification', this.handleNotification.bind(this));
        this.checkBootTokenAndReset();
            await this.refreshOrderDetails();
            this.initZoomFromStorage();
            this.loadCompletedWindow();
        });

        onMounted(() => {
            // One-time fetch only; rely on bus + live deltas afterwards
            // No periodic auto-refresh
        });
    }

    /**
     * Start auto-refresh timer
     */
    // startAutoRefresh removed: one-time fetch + bus updates only

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
                  // Clear persisted live state for the previous session
                  try {
                      window.localStorage.removeItem(liveTicketsKey(sid));
                      window.localStorage.removeItem(liveLinesKey(sid));
                      window.localStorage.removeItem(pressCountsKey(sid));
                  } catch (_) { /* ignore */ }
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
              // Clear persisted live tickets/lines
              try {
                  window.localStorage.removeItem(liveTicketsKey(sid));
                  window.localStorage.removeItem(liveLinesKey(sid));
              } catch (_) { /* ignore */ }
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
            return;
        }
        // Live delta push from POS
        if (payload && payload.type === 'kitchen_delta') {
            try {
                const sid = this.state.shop_id || sessionStorage.getItem('shop_id');
                if (Number(payload.shop_id) !== Number(sid)) return;
                this.appendLiveDeltaTicket(payload);
            } catch (_) { /* ignore */ }
        }
        // Resolution push: replace virtual ids with real line_ids for this ticket
        if (payload && payload.type === 'kitchen_ticket_resolved') {
            try {
                const sid = this.state.shop_id || sessionStorage.getItem('shop_id');
                if (Number(payload.shop_id) !== Number(sid)) return;
                const uid = String(payload.ticket_uid || '');
                const realIds = (payload.line_ids || []).map((n) => Number(n)).filter((n) => Number.isFinite(n) && n > 0);
                if (uid && realIds.length) {
                    const t = (this.state.tickets || []).find((x) => String(x.ticket_uid || '') === uid);
                    if (t) {
                        t.lines = realIds;
                        this.recomputeTicketCounts();
                        const live = (this.state.tickets || []).filter((x) => String(x.ticket_uid || '').startsWith('ticket-live-'));
                        const liveLines = (this.state.lines || []).filter((l) => typeof l?.id === 'number' && l.id < 0);
                        const sid2 = this.state.shop_id || sessionStorage.getItem('shop_id');
                        saveLiveState(sid2, live, liveLines);
                    }
                }
            } catch (_) { /* ignore */ }
        }
        // Session lifecycle events
        if (payload && payload.type === 'kitchen_session_closed') {
            try {
                const sid = this.state.shop_id || sessionStorage.getItem('shop_id');
                if (Number(payload.shop_id) !== Number(sid)) return;
                // Clear persisted and in-memory live state
                try {
                    window.localStorage.removeItem(liveTicketsKey(sid));
                    window.localStorage.removeItem(liveLinesKey(sid));
                    window.localStorage.removeItem(pressCountsKey(sid));
                } catch (_) { /* ignore */ }
                this.state.tickets = (this.state.tickets || []).filter((t) => !(String(t.ticket_uid||'').startsWith('ticket-live-')));
                this.state.lines = (this.state.lines || []).filter((l) => !(typeof l?.id === 'number' && l.id < 0));
                this.recomputeTicketCounts();
            } catch (_) { /* ignore */ }
        }
        if (payload && payload.type === 'kitchen_session_opened') {
            try {
                const sid = this.state.shop_id || sessionStorage.getItem('shop_id');
                if (Number(payload.shop_id) !== Number(sid)) return;
                // Clear any persisted live state from a previous session and refresh
                try {
                    window.localStorage.removeItem(liveTicketsKey(sid));
                    window.localStorage.removeItem(liveLinesKey(sid));
                    window.localStorage.removeItem(pressCountsKey(sid));
                } catch (_) { /* ignore */ }
                await this.refreshOrderDetails();
            } catch (_) { /* ignore */ }
        }
    }

    appendLiveDeltaTicket(payload) {
        try {
            const items = Array.isArray(payload.items) ? payload.items : [];
            if (!items.length) return;
            const orderMeta = payload.meta || {};
            const sid = this.state.shop_id || sessionStorage.getItem('shop_id');
            const press = loadPressCounts(sid);
            const orderRef = String(payload.order_ref || '');
            const currentIndex = Number(press[orderRef] || 0);
            const vIds = [];
            for (const entry of items) {
                const qty = Number(entry && entry.quantity) || 0;
                if (qty <= 0) continue;
                const v = {
                    id: __deltaVirtualId--,
                    full_product_name: (entry && (entry.product_name || entry.name)) || 'Item',
                    qty: qty,
                    order_status: 'waiting',
                    is_modifier: false,
                    is_topping: false,
                    sh_is_topping: false,
                    product_is_topping: false,
                    product_sh_is_topping: false,
                    sh_is_has_topping: false,
                    note: entry && entry.note || '',
                };
                this.state.lines.push(v);
                vIds.push(v.id);
            }
            if (!vIds.length) return;
            const ticket = {
                id: 0,
                pos_reference: payload.order_ref || '',
                partner_id: orderMeta.partner ? [0, orderMeta.partner] : null,
                table_id: Array.isArray(orderMeta.table_id) ? orderMeta.table_id : null,
                floor: orderMeta.floor || '',
                order_type: orderMeta.order_type || '',
                is_online_order: !!orderMeta.is_online_order,
                order_status: 'waiting',
                ticket_uid: payload.ticket_uid || `ticket-live-${Date.now()}`,
                ticket_created_at: new Date().toISOString(),
                lines: vIds,
                kitchen_press_index: currentIndex,
            };
            this.state.tickets = [ticket, ...(this.state.tickets || [])];
            this.recomputeTicketCounts();
            // bump press index and persist
            press[orderRef] = currentIndex + 1;
            savePressCounts(sid, press);
            const currentLiveTickets = (this.state.tickets || []).filter((t) => String(t.ticket_uid || '').startsWith('ticket-live-'));
            const currentLiveLines = (this.state.lines || []).filter((l) => typeof l?.id === 'number' && l.id < 0);
            saveLiveState(sid, currentLiveTickets, currentLiveLines);
        } catch (e) {
            if (__KITCHEN_DEBUG__) console.error('appendLiveDeltaTicket failed', e);
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
            const sid = this.state.shop_id || sessionStorage.getItem('shop_id');
            const prevTickets = Array.isArray(this.state.tickets) ? this.state.tickets.slice() : [];
            const prevLines = Array.isArray(this.state.lines) ? this.state.lines.slice() : [];
            const persisted = loadLiveState(sid);
            const details = await this.orderManagement.fetchOrderDetails();
            Object.assign(this.state, details);
            // Preserve live (pushed) virtual lines/tickets when skipping server persistence
            const liveTickets = [...(prevTickets || []), ...(persisted.tickets || [])].filter((t) => {
                const uid = String(t && t.ticket_uid || '');
                const hasVirtual = Array.isArray(t && t.lines) && t.lines.some((id) => Number(id) < 0);
                return uid.startsWith('ticket-live-') || hasVirtual;
            });
            const liveLines = [...(prevLines || []), ...(persisted.lines || [])].filter((l) => typeof l?.id === 'number' && l.id < 0);
            if (liveLines.length) {
                const byId = new Map((this.state.lines || []).map((x) => [x.id, x]));
                for (const v of liveLines) {
                    if (!byId.has(v.id)) {
                        (this.state.lines || []).push(v);
                    }
                }
            }
            if (liveTickets.length) {
                const byUid = new Map();
                for (const t of liveTickets) {
                    const key = String(t && t.ticket_uid || `t-${Math.random()}`);
                    if (!byUid.has(key)) byUid.set(key, t);
                }
                // Prepend unique live tickets, keep server tickets after
                this.state.tickets = [...byUid.values(), ...(this.state.tickets || [])];
            }
            // Resolve live tickets (virtual lines) to real line ids using kitchen_ticket_uid
            try {
                const all = Array.isArray(this.state.lines) ? this.state.lines : [];
                for (const t of this.state.tickets || []) {
                    const uid = String(t && t.ticket_uid || '');
                    if (!uid) continue;
                    // If ticket already has positive ids, skip
                    const hasReal = Array.isArray(t.lines) && t.lines.some((id) => Number(id) > 0);
                    if (hasReal) continue;
                    const ids = all
                        .filter((l) => String(l && l.kitchen_ticket_uid || '') === uid)
                        .map((l) => Number(l.id))
                        .filter((n) => Number.isFinite(n) && n > 0);
                    if (ids.length) {
                        t.lines = ids;
                    }
                }
            } catch (_) { /* ignore */ }
            this.recomputeTicketCounts();
            // Persist back merged live state
            const currentLiveTickets = (this.state.tickets || []).filter((t) => String(t.ticket_uid || '').startsWith('ticket-live-'));
            const currentLiveLines = (this.state.lines || []).filter((l) => typeof l?.id === 'number' && l.id < 0);
            saveLiveState(sid, currentLiveTickets, currentLiveLines);

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
        if (!order) return [];
        // Prefer per-ticket summary when available (built from log snapshots)
        if (Array.isArray(order.ticket_summary)) {
            return order.ticket_summary;
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


    buildTickets(orders) {
        // Build one ticket per order using all current order lines
        return (orders || [])
            .map((order) => ({
                ...order,
                ticket_uid: `order-${order.id}`,
                ticket_created_at: order.write_date,
                lines: Array.isArray(order.lines) ? order.lines.slice() : [],
            }))
            .filter((t) => Array.isArray(t.lines) && t.lines.length);
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
        // Discrete zoom presets (width x height + font scale)
        // widths:  [260, 300, 320, 380, 440]
        // heights: [400, 500, 520, 520, 540]
        // font scale Option A: [0.92, 0.97, 1.00, 1.08, 1.16]
        return [
            { w: 260, h: 400, s: 0.92 }, // xs (denser)
            { w: 340, h: 520, s: 1.00 }, // default
            { w: 380, h: 520, s: 1.08 }, // large
            { w: 460, h: 540, s: 1.2 }, // xlarge (readable)
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

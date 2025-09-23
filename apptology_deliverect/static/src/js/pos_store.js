/** @odoo-module **/

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { patch } from "@web/core/utils/patch";

// Keep references to possible originals to wrap safely if present
const __origSyncA = PosStore.prototype._syncTableOrdersFromServer;
const __origSyncB = PosStore.prototype.syncTableOrdersFromServer;

function dedupeById(array) {
    if (!Array.isArray(array)) return array;
    const seen = new Set();
    const out = [];
    for (const o of array) {
        const id = o && typeof o === 'object' ? o.id : o;
        if (id == null) { out.push(o); continue; }
        if (seen.has(id)) continue;
        seen.add(id);
        out.push(o);
    }
    return out;
}

patch(PosStore.prototype, {
    /**
     * Fetches new online orders.
     */
    async get_online_orders() {
        try {
            const new_orders = await this.orm.call("pos.order", "get_new_orders", [], { config_id: this.config.id });
            return new_orders;
        } catch (error) {
            console.error("Error fetching new online orders:", error);
        }
    },

    /**
     * Internal: ensure order arrays have unique ids and avoid transient duplicates.
     */
    _applyOrdersDedupe() {
        if (Array.isArray(this.pos_orders)) this.pos_orders = dedupeById(this.pos_orders);
        if (Array.isArray(this.table_orders)) this.table_orders = dedupeById(this.table_orders);
        return true;
    },

    /**
     * Prevent overlapping fetches that can cause transient duplicates.
     */
    async _withOrdersFetchLock(exec) {
        if (this.__ordersFetchInFlight) return this.__ordersFetchInFlight;
        const p = Promise.resolve().then(exec).finally(() => { this.__ordersFetchInFlight = null; });
        this.__ordersFetchInFlight = p;
        return p;
    },

    /**
     * Wrap core sync methods (if present) to dedupe results and avoid overlaps.
     */
    async _syncTableOrdersFromServer() {
        if (typeof __origSyncA === 'function') {
            return this._withOrdersFetchLock(async () => {
                const res = await __origSyncA.apply(this, arguments);
                this._applyOrdersDedupe();
                return res;
            });
        }
        // Fallback to other method if only that exists
        if (typeof __origSyncB === 'function') {
            return this._withOrdersFetchLock(async () => {
                const res = await __origSyncB.apply(this, arguments);
                this._applyOrdersDedupe();
                return res;
            });
        }
        // Nothing to do
        return undefined;
    },

    async syncTableOrdersFromServer() {
        if (typeof __origSyncB === 'function') {
            return this._withOrdersFetchLock(async () => {
                const res = await __origSyncB.apply(this, arguments);
                this._applyOrdersDedupe();
                return res;
            });
        }
        // Fallback to the other if only that exists
        if (typeof __origSyncA === 'function') {
            return this._withOrdersFetchLock(async () => {
                const res = await __origSyncA.apply(this, arguments);
                this._applyOrdersDedupe();
                return res;
            });
        }
        return undefined;
    },
});

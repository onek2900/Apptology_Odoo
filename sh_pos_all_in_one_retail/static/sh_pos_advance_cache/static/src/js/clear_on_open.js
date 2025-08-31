/** @odoo-module */

// Clear POS advance cache when POS app loads
(function () {
    try {
        // Remove localStorage flags so loaders fetch fresh data
        try { localStorage.removeItem('Products'); } catch (e) {}
        try { localStorage.removeItem('Customers'); } catch (e) {}

        // Delete the IndexedDB database used by the advance cache
        if (window.indexedDB && typeof window.indexedDB.deleteDatabase === 'function') {
            window.indexedDB.deleteDatabase('Softhealer_pos');
        }
    } catch (e) {
        // Non-fatal; just log and continue POS load
        console.warn('POS cache clear on open failed', e);
    }
})();


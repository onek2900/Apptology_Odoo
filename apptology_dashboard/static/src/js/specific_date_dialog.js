/**
 * Prompt a specific date and return [startOfDayISO, endOfDayISO]
 * in the user timezone. Minimal and safe outside Owl components.
 * Exposes global: window.apptologyOpenSpecificDateDialog
 */
(function () {
    function openSpecificDateDialog() {
        const DateTime = (window.luxon && window.luxon.DateTime) || null;
        if (!DateTime) {
            const today = new Date();
            const yyyy = today.getFullYear();
            const mm = String(today.getMonth() + 1).padStart(2, '0');
            const dd = String(today.getDate()).padStart(2, '0');
            const defaultISO = `${yyyy}-${mm}-${dd}`;
            const chosen = window.prompt("Enter date (YYYY-MM-DD)", defaultISO);
            if (!chosen) throw new Error("cancelled");
            const from = new Date(chosen + 'T00:00:00');
            const to = new Date(chosen + 'T23:59:59');
            return Promise.resolve([from.toISOString(), to.toISOString()]);
        }
        const todayLocal = DateTime.local();
        const defaultISO = todayLocal.toISODate();
        const chosen = window.prompt("Enter date (YYYY-MM-DD)", defaultISO);
        if (!chosen) throw new Error("cancelled");
        const start = DateTime.fromISO(chosen).startOf("day");
        const end = DateTime.fromISO(chosen).endOf("day");
        return Promise.resolve([start.toISO(), end.toISO()]);
    }
    window.apptologyOpenSpecificDateDialog = openSpecificDateDialog;
})();

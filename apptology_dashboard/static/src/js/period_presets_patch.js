/**
 * Apptology: extend Spreadsheet Dashboard period presets with
 * Today, Yesterday, and Specific Date (single-day range).
 *
 * This file uses a DOM enhancement fallback with no ESM imports
 * to avoid asset pipeline issues. A proper component patch is
 * provided in comments below once the exact imports are known.
 */

// Access luxon from global to avoid ESM
const DateTime = (window.luxon && window.luxon.DateTime) || null;

// Utility: compute [start, end] as ISO strings in user tz for convenience
function isoRangeFor(day) {
    const start = day.startOf("day").toISO();
    const end = day.endOf("day").toISO();
    return [start, end];
}

// Soft DOM enhancement that works even before exact component names are confirmed.
// It augments the dropdown options and, if we can find a store/apply function on
// the component instance at runtime, it will apply the date range.
function attachDomEnhancementOnce() {
    if (window.__apptologyDashboardEnhanceAttached) return;
    window.__apptologyDashboardEnhanceAttached = true;

    document.addEventListener("change", async (ev) => {
        const el = ev.target;
        if (!(el instanceof HTMLSelectElement)) return;
        if (!el.classList.contains("date_filter_values")) return;

        if (el.value === "apptology_today") {
            let from, to;
            if (DateTime) {
                [from, to] = isoRangeFor(DateTime.local());
            } else {
                const d = new Date();
                const y = d.toISOString().slice(0, 10);
                from = new Date(`${y}T00:00:00`).toISOString();
                to = new Date(`${y}T23:59:59`).toISOString();
            }
            applyCustomRange(ev.target, from, to);
        } else if (el.value === "apptology_yesterday") {
            let from, to;
            if (DateTime) {
                [from, to] = isoRangeFor(DateTime.local().minus({ days: 1 }));
            } else {
                const d = new Date();
                d.setDate(d.getDate() - 1);
                const y = d.toISOString().slice(0, 10);
                from = new Date(`${y}T00:00:00`).toISOString();
                to = new Date(`${y}T23:59:59`).toISOString();
            }
            applyCustomRange(ev.target, from, to);
        } else if (el.value === "apptology_specific_date") {
            try {
                const [from, to] = await (window.apptologyOpenSpecificDateDialog
                    ? window.apptologyOpenSpecificDateDialog()
                    : Promise.reject(new Error("dialog unavailable")));
                applyCustomRange(ev.target, from, to);
            } catch (_) {
                // cancelled
            }
        }
    }, { capture: true });

    // Insert our options into the select when it appears
    const obs = new MutationObserver(() => {
        for (const sel of document.querySelectorAll('select.date_filter_values')) {
            if (sel.querySelector('option[value="apptology_today"]')) continue;

            const oToday = document.createElement("option");
            oToday.value = "apptology_today";
            oToday.textContent = (window._t || ((s) => s))("Today");

            const oYest = document.createElement("option");
            oYest.value = "apptology_yesterday";
            oYest.textContent = (window._t || ((s) => s))("Yesterday");

            const oSpec = document.createElement("option");
            oSpec.value = "apptology_specific_date";
            oSpec.textContent = (window._t || ((s) => s))("Specific Date…");

            // After the placeholder option, before other presets.
            if (sel.options.length) {
                sel.insertBefore(oToday, sel.options[1] || null);
                sel.insertBefore(oYest, sel.options[2] || null);
                sel.insertBefore(oSpec, sel.options[3] || null);
            } else {
                sel.append(oToday, oYest, oSpec);
            }
        }
    });
    obs.observe(document.documentElement, { childList: true, subtree: true });
}

// Try to locate an API on the component or environment to apply a custom date range.
// This is a best-effort fallback until we patch the actual component method below.
function applyCustomRange(selectEl, dateFromISO, dateToISO) {
    // If a component instance is bound on the select, try common method names.
    const comp = (selectEl.__owl__ && selectEl.__owl__.parent) || null;
    if (comp) {
        for (const meth of ["setDateRange", "onChangePeriod", "applyPeriod", "setPeriod"]) {
            if (typeof comp[meth] === "function") {
                try {
                    comp[meth]({ dateFrom: dateFromISO, dateTo: dateToISO, key: "apptology_custom_day" });
                    return;
                } catch (_) {}
            }
        }
        // Look for a store on the component env
        const maybeStore = comp.env && (comp.env.dashboardStore || comp.env.store || (comp.env.services && comp.env.services.dashboard));
        for (const meth of ["setDateRange", "setDateFilter", "applyDateFilter"]) {
            if (maybeStore && typeof maybeStore[meth] === "function") {
                try {
                    maybeStore[meth]({ dateFrom: dateFromISO, dateTo: dateToISO });
                    return;
                } catch (_) {}
            }
        }
    }

    // Last resort: dispatch a custom event that other code can handle.
    selectEl.dispatchEvent(new CustomEvent("apptology:spreadsheet_dashboard:setDateRange", {
        bubbles: true,
        detail: { dateFrom: dateFromISO, dateTo: dateToISO },
    }));
}

attachDomEnhancementOnce();

// --- Preferred approach (to finalize after you locate exact component) ---
// Example of how to patch a discovered PeriodSelector component that maps keys
// to ranges. Replace the import above and the class name below, then uncomment.
//
// import { patch } from "@web/core/utils/patch";
// import { PeriodSelector } from "@spreadsheet_dashboard/components/period_selector/period_selector";
// patch(PeriodSelector.prototype, "apptology_dashboard.period_presets", {
//     get presets() {
//         const base = super.presets ? super.presets : [];
//         return [
//             { key: "apptology_today", label: this.env._t("Today") },
//             { key: "apptology_yesterday", label: this.env._t("Yesterday") },
//             { key: "apptology_specific_date", label: this.env._t("Specific Date…") },
//             ...base,
//         ];
//     },
//
//     async onChangePeriod(evOrKey) {
//         const key = typeof evOrKey === "string" ? evOrKey : evOrKey.target.value;
//         if (key === "apptology_today") {
//             const [from, to] = isoRangeFor(DateTime.local());
//             return this.env.dashboardStore.setDateRange({ dateFrom: from, dateTo: to });
//         }
//         if (key === "apptology_yesterday") {
//             const [from, to] = isoRangeFor(DateTime.local().minus({ days: 1 }));
//             return this.env.dashboardStore.setDateRange({ dateFrom: from, dateTo: to });
//         }
//         if (key === "apptology_specific_date") {
//             const [from, to] = await window.apptologyOpenSpecificDateDialog();
//             return this.env.dashboardStore.setDateRange({ dateFrom: from, dateTo: to });
//         }
//         return super.onChangePeriod ? super.onChangePeriod(evOrKey) : undefined;
//     },
// });


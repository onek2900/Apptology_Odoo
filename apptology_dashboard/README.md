Apptology Dashboard (Odoo 17)
================================

Goal
----
Extend the Spreadsheet Dashboard period dropdown with:
- Today
- Yesterday
- Specific Date (single-day range, 00:00–23:59 in user timezone)

This addon only loads frontend assets and patches the dashboard in place.

How to find the period component and keys
----------------------------------------
1) Enable Developer Mode with assets:
   - In Odoo, append `?debug=assets` to the URL (or enable from Settings → Developer Tools).

2) Open the Spreadsheet Dashboard view and DevTools → Sources tab.

3) Find the component/template:
   - Use global search (Ctrl/Cmd+Shift+F) for `date_filter_values` or any option label like `Last 90 Days`.
   - You should land in a JS/TS or XML file under a path similar to:
     `addons/spreadsheet_dashboard/static/src/.../period_selector.*`
     or `.../filters/date_filter.*`.
   - Note the exported class/function name (e.g., `PeriodSelector`, `DateFilter`) and the file import path.

4) Find how presets are mapped to ranges:
   - Look for an array/object of presets (e.g., `PRESETS`, `PERIODS`) or a switch/case in a handler like `onChangePeriod`.
   - Observe what is called to apply the chosen range, commonly something like:
     `this.env.dashboardStore.setDateRange({ dateFrom, dateTo })`
     or `store.setDateFilter(...)`.
   - Confirm the parameter keys (usually `dateFrom` / `dateTo` as ISO strings) by watching Network/XHR calls after choosing a built-in preset.

Implementing the precise patch
------------------------------
1) Update the import in `static/src/js/period_presets_patch.js` to point to the actual component you found, e.g.:

   ```js
   import { PeriodSelector } from "@spreadsheet_dashboard/components/period_selector/period_selector";
   ```

2) Uncomment the `patch(PeriodSelector.prototype, ...)` block and ensure the method names match what the component exposes (`presets`, `onChangePeriod`, etc.).

3) Confirm the store call:
   - If the component uses `this.env.dashboardStore.setDateRange({ dateFrom, dateTo })`, keep that.
   - If it uses a different method, adapt accordingly (e.g., `setDateFilter`).

4) Hot-reload and test:
   - Update assets (hard refresh with cache disabled or restart Odoo if needed).
   - Verify new options appear and apply single-day ranges correctly.

About the DOM enhancement fallback
----------------------------------
Until you finalize the exact import/method names, the module adds the three options to the dropdown and tries to apply the range by probing common component/store methods or, as a last resort, emits a custom event `apptology:spreadsheet_dashboard:setDateRange` that you could handle yourself if needed.

Production recommendation
-------------------------
Prefer the explicit component patch once you identify the correct class and store API. Keep the DOM fallback only for resilience during development.


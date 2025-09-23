/** @odoo-module **/

// Normalize printer props without importing the printer service module directly.
// We wrap the 'printer' service via the service registry to maintain compatibility
// across POS variants and asset bundles.

import { registry } from "@web/core/registry";

const services = registry.category("services");
const printerSvc = services.get("printer");

if (printerSvc && typeof printerSvc.start === "function") {
    const origStart = printerSvc.start;
    printerSvc.start = (env, deps) => {
        const svc = origStart(env, deps);
        if (svc && typeof svc.print === "function" && !svc.__apptology_print_wrapped__) {
            const origPrint = svc.print.bind(svc);
            svc.print = function (Component, props, options) {
                try {
                    if (!props || typeof props !== "object") props = {};
                    if (!props.data || typeof props.data !== "object") props.data = {};
                    if (props.is_reciptScreen == null) props.is_reciptScreen = true;
                    if (props.data.is_reciptScreen == null) props.data.is_reciptScreen = true;
                } catch (_) {
                    props = { data: { is_reciptScreen: true }, is_reciptScreen: true };
                }
                return origPrint(Component, props, options);
            };
            svc.__apptology_print_wrapped__ = true;
        }
        return svc;
    };
}

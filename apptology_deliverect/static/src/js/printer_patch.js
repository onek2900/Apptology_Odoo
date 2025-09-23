/** @odoo-module **/

// Normalize printer props for environments where the printer service
// tries to set flags on null props/data. This is safe and no-ops when
// props are already well-formed.

import { patch } from "@web/core/utils/patch";
import { PosPrinterService } from "@point_of_sale/app/services/printer/printer";

const __origPrint = PosPrinterService.prototype.print;

patch(PosPrinterService.prototype, {
    async print(Component, props, options) {
        try {
            if (!props || typeof props !== "object") props = {};
            if (!props.data || typeof props.data !== "object") props.data = {};
            // Some implementations expect this flag on either root or data
            if (props.is_reciptScreen == null) props.is_reciptScreen = true;
            if (props.data.is_reciptScreen == null) props.data.is_reciptScreen = true;
        } catch (e) {
            // Last-resort guard: never let printing crash due to props shape
            props = { data: { is_reciptScreen: true }, is_reciptScreen: true };
        }
        return __origPrint.call(this, Component, props, options);
    },
});


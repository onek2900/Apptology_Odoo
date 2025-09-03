/** @odoo-module **/

import { WebClient } from "@web/webclient/webclient";
import { patch } from "@web/core/utils/patch";
import { loadJS } from "@web/core/assets";
import { useService } from "@web/core/utils/hooks";

let gplacesBootstrapping;

async function ensureGooglePlacesLoaded(rpc) {
    if (window.google && window.google.maps && window.google.maps.places) return true;
    if (!gplacesBootstrapping) {
        const apiKey = await rpc("/web/dataset/call_kw", {
            model: "ir.config_parameter",
            method: "get_param",
            args: ["apptology_address_autofill.google_places_api_key", ""],
            kwargs: {},
        });
        if (!apiKey) {
            console.warn("[GPlaces] API key missing: apptology_address_autofill.google_places_api_key");
            return false;
        }
        const url = `https://maps.googleapis.com/maps/api/js?key=${encodeURIComponent(apiKey)}&libraries=places&loading=async`;
        gplacesBootstrapping = loadJS(url).catch((e) => {
            console.error("[GPlaces] Failed to load Google Maps JS", e);
            gplacesBootstrapping = undefined;
        });
    }
    await gplacesBootstrapping;
    return !!(window.google && window.google.maps && window.google.maps.places);
}

const superSetup = WebClient.prototype.setup;
patch(WebClient.prototype, "apptology_address_autofill_gplaces_bootstrap", {
    setup() {
        superSetup && superSetup.apply(this, arguments);
        this.rpc = useService("rpc");
        // Fire and forget; ensures the library is present early in backend UI
        ensureGooglePlacesLoaded(this.rpc);
    },
});


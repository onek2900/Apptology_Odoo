/** @odoo-module **/

import { registry } from "@web/core/registry";

// We avoid deep POS class dependencies by observing the DOM
// and attaching Google Places Autocomplete to the street input
// in the Partner editor when present.

let googleScriptLoading = null;

async function loadGooglePlaces(apiKey) {
    if (window.google && window.google.maps && window.google.maps.places) {
        console.info("[POS Places] Google Places already loaded");
        return;
    }
    if (!apiKey) return;
    if (!googleScriptLoading) {
        console.info("[POS Places] Injecting Google Maps script");
        googleScriptLoading = new Promise((resolve, reject) => {
            const script = document.createElement("script");
            script.src = `https://maps.googleapis.com/maps/api/js?key=${encodeURIComponent(apiKey)}&libraries=places`;
            script.async = true;
            script.defer = true;
            script.onload = () => resolve();
            script.onerror = (e) => reject(e);
            document.head.appendChild(script);
        });
    }
    return googleScriptLoading;
}

async function fetchPlacesKey(rpc) {
    try {
        const res = await rpc("/apptology_address_autofill/places_key", {});
        return res || { enabled: false, api_key: "" };
    } catch (e) {
        return { enabled: false, api_key: "" };
    }
}

function findInput(selector) {
    // limit to POS app container if present
    const appRoot = document.querySelector(".pos, .o_pos_app, .o_web_client");
    return (appRoot || document).querySelector(selector);
}

function setInputValue(selector, value) {
    const el = findInput(selector);
    if (el) {
        el.value = value || "";
        el.dispatchEvent(new Event("input", { bubbles: true }));
        el.dispatchEvent(new Event("change", { bubbles: true }));
    }
}

function parseAddress(place) {
    const out = { street: "", street2: "", city: "", state_name: "", country_name: "", zip: "" };
    if (!place || !place.address_components) return out;
    const comps = place.address_components;
    const get = (type) => comps.find((c) => c.types.includes(type));
    const streetNumber = get("street_number")?.long_name || "";
    const route = get("route")?.long_name || "";
    const subpremise = get("subpremise")?.long_name || "";
    out.street = [streetNumber, route].filter(Boolean).join(" ");
    out.street2 = subpremise;
    out.city = get("locality")?.long_name || get("sublocality")?.long_name || "";
    out.state_name = get("administrative_area_level_1")?.long_name || "";
    out.country_name = get("country")?.long_name || "";
    out.zip = get("postal_code")?.long_name || "";
    return out;
}

function attachAutocompleteToStreet() {
    const streetInput = findInput('input[name="street"], input[data-name="street"], input.o_input[name="street"]');
    if (!streetInput || streetInput.__hasAutocomplete) return;
    if (!(window.google && window.google.maps && window.google.maps.places)) return;
    console.info("[POS Places] Attaching autocomplete to street input");
    const autocomplete = new window.google.maps.places.Autocomplete(streetInput, {
        fields: ["address_components", "geometry", "formatted_address"],
        types: ["address"],
    });
    streetInput.__hasAutocomplete = true;
    autocomplete.addListener("place_changed", () => {
        const place = autocomplete.getPlace();
        const addr = parseAddress(place);
        setInputValue('input[name="street"], input[data-name="street"]', addr.street);
        setInputValue('input[name="street2"], input[data-name="street2"]', addr.street2);
        setInputValue('input[name="city"], input[data-name="city"]', addr.city);
        setInputValue('input[name="zip"], input[data-name="zip"]', addr.zip);
        // Best-effort: set text fields for state/country if present as inputs.
        setInputValue('input[name="state_name"], input[data-name="state_name"]', addr.state_name);
        setInputValue('input[name="country_name"], input[data-name="country_name"]', addr.country_name);
    });
}

function initObserver() {
    const observer = new MutationObserver(() => attachAutocompleteToStreet());
    observer.observe(document.body, { childList: true, subtree: true });
    // Try once immediately as well
    attachAutocompleteToStreet();
    return observer;
}

// Register a small service that initializes the script and observer when POS boots
registry.category("services").add(
    "apptology_pos_places_boot",
    {
        dependencies: ["rpc"],
        start: async (env, { rpc }) => {
            console.info("[POS Places] Service starting");
            const { enabled, api_key } = await fetchPlacesKey(rpc);
            console.info("[POS Places] Settings", { enabled, hasKey: Boolean(api_key) });
            if (!enabled || !api_key) return;
            try {
                await loadGooglePlaces(api_key);
                const obs = initObserver();
                return {
                    stop() {
                        try {
                            obs.disconnect();
                        } catch (_) {}
                    },
                };
            } catch (e) {
                console.warn("[POS Places] Failed to initialize", e);
            }
        },
    }
);

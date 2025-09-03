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

function isVisible(el) {
    if (!el) return false;
    const style = window.getComputedStyle(el);
    return style && style.display !== 'none' && style.visibility !== 'hidden' && el.offsetParent !== null;
}

function findInput(selector) {
    // limit to POS app container if present
    const appRoot = document.querySelector(".pos, .o_pos_app, .o_web_client");
    return (appRoot || document).querySelector(selector);
}

function findByLabel(possibleLabels) {
    const labels = Array.from(document.querySelectorAll('label, .o_form_label'));
    for (const expected of possibleLabels) {
        const lab = labels.find((l) => new RegExp(`\\b${expected}\\b`, 'i').test(l.textContent || ''));
        if (lab) {
            const container = lab.closest('.o_form_group, .o_group, .o_row, div');
            const input = container && container.querySelector('input, textarea, select');
            if (input && isVisible(input)) return input;
        }
    }
    return null;
}

function findGenericField(candidates, labelCandidates = []) {
    for (const sel of candidates) {
        const el = findInput(sel);
        if (el && isVisible(el)) return el;
    }
    if (labelCandidates.length) {
        const el = findByLabel(labelCandidates);
        if (el) return el;
    }
    return null;
}

function findStreetInput() {
    return findGenericField([
        'input[name="street"]',
        'input[data-name="street"]',
        'input.o_input[name="street"]',
        'div[name="street"] input',
        'input[aria-label*="Street" i]',
        'input[placeholder*="Street" i]'
    ], ['Street']);
}

function findCityInput() {
    return findGenericField([
        'input[name="city"]',
        'input[data-name="city"]',
        'input[placeholder*="City" i]',
        'input[aria-label*="City" i]'
    ], ['City']);
}

function findZipInput() {
    return findGenericField([
        'input[name="zip"]',
        'input[data-name="zip"]',
        'input[name="postal"]',
        'input[name="postcode"]',
        'input[placeholder*="Zip" i]',
        'input[placeholder*="Postal" i]',
        'input[placeholder*="Postcode" i]',
        'input[aria-label*="Zip" i]',
        'input[aria-label*="Postal" i]'
    ], ['Zip', 'Postal Code', 'Postcode']);
}

function findStreet2Input() {
    return findGenericField([
        'input[name="street2"]',
        'input[data-name="street2"]',
        'input[placeholder*="Apt" i]',
        'input[placeholder*="Suite" i]',
        'input[placeholder*="Unit" i]'
    ], ['Street 2', 'Apartment', 'Suite', 'Unit']);
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
    const out = { street: "", street2: "", city: "", state_name: "", country_name: "", zip: "", state_code: "", country_code: "" };
    if (!place || !place.address_components) return out;
    const comps = place.address_components;
    const get = (type) => comps.find((c) => c.types.includes(type));
    const streetNumber = get("street_number")?.long_name || "";
    const route = get("route")?.long_name || "";
    const subpremise = get("subpremise")?.long_name || "";
    out.street = [streetNumber, route].filter(Boolean).join(" ");
    out.street2 = subpremise;
    out.city = get("locality")?.long_name
        || get("postal_town")?.long_name
        || get("sublocality_level_1")?.long_name
        || get("sublocality")?.long_name
        || "";
    const stateComp = get("administrative_area_level_1");
    out.state_name = stateComp?.long_name || "";
    out.state_code = stateComp?.short_name || "";
    const countryComp = get("country");
    out.country_name = countryComp?.long_name || "";
    out.country_code = countryComp?.short_name || "";
    out.zip = get("postal_code")?.long_name || "";
    return out;
}

function attachAutocompleteToStreet() {
    const streetInput = findStreetInput();
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
        // Delay slightly to override Google's formatted address write
        setTimeout(() => {
            const street2 = findStreet2Input();
            const city = findCityInput();
            const zip = findZipInput();
            setInputValue('input[name="street"], input[data-name="street"]', addr.street);
            if (street2) { street2.value = addr.street2 || ''; street2.dispatchEvent(new Event('input', {bubbles:true})); street2.dispatchEvent(new Event('change', {bubbles:true})); }
            if (city) { city.value = addr.city || ''; city.dispatchEvent(new Event('input', {bubbles:true})); city.dispatchEvent(new Event('change', {bubbles:true})); }
            if (zip) { zip.value = addr.zip || ''; zip.dispatchEvent(new Event('input', {bubbles:true})); zip.dispatchEvent(new Event('change', {bubbles:true})); }
        }, 50);
        // Best-effort: set text fields for state/country if present as inputs.
        setInputValue('input[name="state_name"], input[data-name="state_name"]', addr.state_name);
        setInputValue('input[name="country_name"], input[data-name="country_name"]', addr.country_name);
        // Resolve and set real Odoo many2one for country/state when possible
        resolveAndApplyCountryState(addr);
    });

    // Compliance badge
    ensurePoweredByGoogleBadge(streetInput);
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
            window.__apptology_pos_places_rpc__ = rpc; // expose for helper usage
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

async function resolveAndApplyCountryState(addr) {
    const rpc = window.__apptology_pos_places_rpc__;
    if (!rpc) return;
    try {
        let countryId = null;
        if (addr.country_code) {
            const res = await rpc('/web/dataset/call_kw', {
                model: 'res.country',
                method: 'search_read',
                args: [[['code', '=', addr.country_code]]],
                kwargs: { fields: ['id', 'name', 'code'], limit: 1 },
            });
            if (res && res.length) countryId = res[0].id;
        }
        if (!countryId && addr.country_name) {
            const res = await rpc('/web/dataset/call_kw', {
                model: 'res.country',
                method: 'search_read',
                args: [[['name', 'ilike', addr.country_name]]],
                kwargs: { fields: ['id', 'name', 'code'], limit: 1 },
            });
            if (res && res.length) countryId = res[0].id;
        }

        if (countryId) {
            applyMany2OneSelection('country_id', countryId, addr.country_name || addr.country_code);
        }

        let stateId = null;
        if (addr.state_code) {
            const res = await rpc('/web/dataset/call_kw', {
                model: 'res.country.state',
                method: 'search_read',
                args: [[['code', '=', addr.state_code], ['country_id', '=', countryId]]],
                kwargs: { fields: ['id', 'name', 'code', 'country_id'], limit: 1 },
            });
            if (res && res.length) stateId = res[0].id;
        }
        if (!stateId && addr.state_name) {
            const res = await rpc('/web/dataset/call_kw', {
                model: 'res.country.state',
                method: 'search_read',
                args: [[['name', 'ilike', addr.state_name], ['country_id', '=', countryId]]],
                kwargs: { fields: ['id', 'name', 'code', 'country_id'], limit: 1 },
            });
            if (res && res.length) stateId = res[0].id;
        }

        if (stateId) {
            applyMany2OneSelection('state_id', stateId, addr.state_name || addr.state_code);
        }
    } catch (e) {
        console.warn('[POS Places] Failed to resolve country/state', e);
    }
}

function applyMany2OneSelection(fieldName, id, displayText) {
    // Try select first (some POS themes render selects)
    const select = findInput(`select[name="${fieldName}"]`);
    if (select) {
        select.value = String(id);
        select.dispatchEvent(new Event('change', { bubbles: true }));
        return;
    }
    // Fallback: set text into many2one input
    const m2oInput = findInput(`input[name="${fieldName}"], input[data-name="${fieldName}"]`);
    if (m2oInput) {
        m2oInput.value = displayText || '';
        m2oInput.dispatchEvent(new Event('input', { bubbles: true }));
        m2oInput.dispatchEvent(new Event('change', { bubbles: true }));
    }
}

function ensurePoweredByGoogleBadge(streetInput) {
    try {
        const id = 'apptology-gplaces-badge';
        if (document.getElementById(id)) return;
        const badge = document.createElement('div');
        badge.id = id;
        badge.style.fontSize = '11px';
        badge.style.color = '#5f6368';
        badge.style.marginTop = '4px';
        badge.style.display = 'flex';
        badge.style.alignItems = 'center';
        badge.innerHTML = 'Powered by Google';
        const container = streetInput.closest('.o_form_view, .o_form_renderer, form') || streetInput.parentElement;
        // insert after the input
        (streetInput.parentElement || container).appendChild(badge);
    } catch (_) {}
}

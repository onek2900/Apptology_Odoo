/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { loadJS } from "@web/core/assets";
import { onMounted, onPatched } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { PartnerDetailsEdit } from "@point_of_sale/app/screens/partner/partner_details_edit/partner_details_edit";

let googleScriptLoadingPOS;

async function loadGooglePlacesPOS(rpc) {
    if (window.google && window.google.maps && window.google.maps.places) return;
    if (!googleScriptLoadingPOS) {
        const apiKey = await rpc("/web/dataset/call_kw", {
            model: "ir.config_parameter",
            method: "get_param",
            args: [
                "apptology_address_autofill.google_places_api_key",
                "",
            ],
            kwargs: {},
        });
        if (!apiKey) {
            console.warn("[POS] Google Places API key missing");
            return;
        }
        const url = `https://maps.googleapis.com/maps/api/js?key=${encodeURIComponent(apiKey)}&libraries=places&loading=async`;
        googleScriptLoadingPOS = loadJS(url).catch((e) => {
            console.error("[POS] Failed loading Google Maps script", e);
            googleScriptLoadingPOS = undefined;
        });
    }
    await googleScriptLoadingPOS;
}

function setInputValue(input, value) {
    if (!input) return;
    input.value = value || "";
    input.dispatchEvent(new Event("input", { bubbles: true }));
    input.dispatchEvent(new Event("change", { bubbles: true }));
}

function findInputCI(root, targetName) {
    const t = String(targetName || "").toLowerCase();
    const nodes = root?.querySelectorAll?.('input[name], textarea[name]') || [];
    for (const n of nodes) {
        const nameAttr = (n.getAttribute('name') || '').toLowerCase();
        if (nameAttr === t) return n;
    }
    return null;
}

function findSelectCI(root, targetName) {
    const t = String(targetName || "").toLowerCase();
    const nodes = root?.querySelectorAll?.('select[name]') || [];
    for (const n of nodes) {
        const nameAttr = (n.getAttribute('name') || '').toLowerCase();
        if (nameAttr === t) return n;
    }
    return null;
}

function ensureSearchInput(el) {
    // Try to find existing dedicated search input
    let input = el.querySelector('input[name="gplaces_search"]');
    if (input) return input;
    // Insert a new input above the street field
    const streetInput = findInputCI(el, 'street');
    if (!streetInput) return null;
    const group = streetInput.closest('div, .o_field_widget') || streetInput.parentElement;
    input = document.createElement('input');
    input.type = 'text';
    input.name = 'gplaces_search';
    input.placeholder = 'Search address...';
    input.className = streetInput.className || 'o_input';
    input.style.marginBottom = '6px';
    group.parentElement?.insertBefore(input, group);
    return input;
}

async function bindPOSAutocomplete(component) {
    await loadGooglePlacesPOS(component.rpc);
    if (!(window.google && window.google.maps && window.google.maps.places)) return;

    const el = component.el;
    if (!el) return;
    const searchInput = ensureSearchInput(el);
    if (!searchInput || searchInput.__gplaces_bound) return;
    searchInput.__gplaces_bound = true;
    searchInput.setAttribute("autocomplete", "off");

    const autocomplete = new window.google.maps.places.Autocomplete(searchInput, {
        types: ["address"],
        fields: ["address_components", "geometry", "formatted_address"],
    });

    autocomplete.addListener("place_changed", async () => {
        const place = autocomplete.getPlace();
        if (!place || !place.address_components) return;
        const comp = {};
        for (const c of place.address_components) {
            for (const t of c.types) comp[t] = c;
        }
        const streetNumber = comp["street_number"]?.long_name || "";
        const route = comp["route"]?.long_name || "";
        const street = [streetNumber, route].filter(Boolean).join(" ");
        const city = (
            comp["locality"]?.long_name ||
            comp["postal_town"]?.long_name ||
            comp["administrative_area_level_2"]?.long_name ||
            ""
        );
        const zip = comp["postal_code"]?.long_name || "";
        const street2Parts = [
            comp["sublocality"]?.long_name,
            comp["sublocality_level_1"]?.long_name,
            comp["premise"]?.long_name,
            comp["neighborhood"]?.long_name,
        ].filter(Boolean);
        const street2 = street2Parts.join(", ");

        // Fill simple inputs directly
        const streetInput = findInputCI(el, 'street');
        setInputValue(streetInput, street);
        setInputValue(findInputCI(el, 'street2'), street2);
        setInputValue(findInputCI(el, 'city'), city);
        setInputValue(findInputCI(el, 'zip'), zip);

        // Resolve country/state by RPC then set select inputs if present
        const countryName = comp["country"]?.long_name;
        const countryCode = comp["country"]?.short_name;
        const stateName = comp["administrative_area_level_1"]?.long_name;
        const stateCode = comp["administrative_area_level_1"]?.short_name;
        try {
            let countryId;
            if (countryName || countryCode) {
                const countries = await component.rpc("/web/dataset/call_kw", {
                    model: "res.country",
                    method: "search_read",
                    args: [[
                        "|",
                        ["code", "=", countryCode || ""],
                        ["name", "ilike", countryName || ""],
                    ]],
                    kwargs: { fields: ["id", "name", "code"] },
                });
                if (countries?.length) countryId = countries[0].id;
            }
            if (countryId) {
                const countrySelect = findSelectCI(el, 'country_id');
                if (countrySelect) {
                    countrySelect.value = String(countryId);
                    countrySelect.dispatchEvent(new Event("change", { bubbles: true }));
                }
                if (stateName || stateCode) {
                    const states = await component.rpc("/web/dataset/call_kw", {
                        model: "res.country.state",
                        method: "search_read",
                        args: [[
                            ["country_id", "=", countryId],
                            "|",
                            ["code", "=", stateCode || ""],
                            ["name", "ilike", stateName || ""],
                        ]],
                        kwargs: { fields: ["id", "name", "code", "country_id"] },
                    });
                    if (states?.length) {
                        const stateSelect = findSelectCI(el, 'state_id');
                        if (stateSelect) {
                            stateSelect.value = String(states[0].id);
                            stateSelect.dispatchEvent(new Event("change", { bubbles: true }));
                        }
                    }
                }
            }
        } catch (e) {
            console.warn("[POS] country/state resolve failed", e);
        }
    });
}

const superSetup = PartnerDetailsEdit.prototype.setup;
patch(PartnerDetailsEdit.prototype, {
    setup() {
        superSetup && superSetup.apply(this, arguments);
        this.rpc = useService("rpc");
        const bind = () => bindPOSAutocomplete(this);
        onMounted(bind);
        onPatched(bind);
    },
});

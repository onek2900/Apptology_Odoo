/** @odoo-module **/

import { CharField } from "@web/views/fields/char/char_field";
import { loadJS } from "@web/core/assets";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { onMounted, onPatched } from "@odoo/owl";

let googleScriptLoading;
const dbg = (...args) => {
    try {
        if (window.localStorage && localStorage.getItem("gplaces_debug") === "1") {
            // eslint-disable-next-line no-console
            console.log("[GPlaces]", ...args);
        }
    } catch (_) {}
};

async function loadGooglePlaces(rpc) {
    if (window.google && window.google.maps && window.google.maps.places) {
        return;
    }
    if (!googleScriptLoading) {
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
        console.warn(
            "Google Places API key is not set (apptology_address_autofill.google_places_api_key)."
        );
        return;
    }
        const url = `https://maps.googleapis.com/maps/api/js?key=${encodeURIComponent(
            apiKey
        )}&libraries=places&loading=async`;
        googleScriptLoading = loadJS(url).catch((e) => {
            console.error("Failed loading Google Maps script", e);
            googleScriptLoading = undefined;
        });
    }
    await googleScriptLoading;
}

async function attachPlacesAutocomplete(component, input) {
    if (!input || !(window.google && window.google.maps && window.google.maps.places)) {
        return;
    }
    if (input.__gplaces_bound) return;
    input.__gplaces_bound = true;
    try {
        input.setAttribute("autocomplete", "off");
    } catch (e) {}

    dbg("binding to", component.props?.name, component.props?.record?.resModel);
    const autocomplete = new window.google.maps.places.Autocomplete(input, {
        // Limit to addresses only
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
        const values = {};
        const streetNumber = comp["street_number"]?.long_name || "";
        const route = comp["route"]?.long_name || "";
        const street = [streetNumber, route].filter(Boolean).join(" ");
        if (street) values["street"] = street;
        // City fallbacks: locality -> postal_town -> administrative_area_level_2
        values["city"] = (
            comp["locality"]?.long_name ||
            comp["postal_town"]?.long_name ||
            comp["administrative_area_level_2"]?.long_name ||
            undefined
        );
        if (comp["postal_code"]) values["zip"] = comp["postal_code"].long_name;
        // Optional street2 from sublocality/premise/neighborhood
        const street2Parts = [
            comp["sublocality"]?.long_name,
            comp["sublocality_level_1"]?.long_name,
            comp["premise"]?.long_name,
            comp["neighborhood"]?.long_name,
        ].filter(Boolean);
        if (street2Parts.length) values["street2"] = street2Parts.join(", ");

        const canSet = (name) =>
            component.props.record && component.props.record.activeFields &&
            Object.prototype.hasOwnProperty.call(component.props.record.activeFields, name);

        if (place.geometry && place.geometry.location) {
            const loc = place.geometry.location;
            if (canSet("partner_latitude")) values["partner_latitude"] = loc.lat();
            if (canSet("partner_longitude")) values["partner_longitude"] = loc.lng();
        }

        const rpc = component.rpc;
        const countryName = comp["country"]?.long_name;
        const countryCode = comp["country"]?.short_name;
        const stateName = comp["administrative_area_level_1"]?.long_name;
        const stateCode = comp["administrative_area_level_1"]?.short_name;

        try {
            if (countryName || countryCode) {
                const countries = await rpc("/web/dataset/call_kw", {
                    model: "res.country",
                    method: "search_read",
                    args: [[
                        "|",
                        ["code", "=", countryCode || ""],
                        ["name", "ilike", countryName || ""],
                    ]],
                    kwargs: { fields: ["id", "name", "code"] },
                });
                if (countries && countries.length) {
                    values["country_id"] = countries[0].id;
                }
            }
            if ((stateName || stateCode) && values["country_id"]) {
                const states = await rpc("/web/dataset/call_kw", {
                    model: "res.country.state",
                    method: "search_read",
                    args: [[
                        ["country_id", "=", values["country_id"]],
                        "|",
                        ["code", "=", stateCode || ""],
                        ["name", "ilike", stateName || ""],
                    ]],
                    kwargs: { fields: ["id", "name", "code", "country_id"] },
                });
                if (states && states.length) {
                    values["state_id"] = states[0].id;
                }
            }
        } catch (e) {
            console.warn("Failed resolving country/state", e);
        }

        try {
            await component.props.record.update(values);
            if (street) {
                await component.props.update(street);
            }
            dbg("updated values", values);
        } catch (e) {
            console.error("Failed updating record from Places selection", e);
        }
    });
}

const superSetup = CharField.prototype.setup;
patch(CharField.prototype, {
    setup() {
        // Call original CharField setup safely (no _super dependency)
        superSetup && superSetup.apply(this, arguments);
        this.rpc = useService("rpc");
        const bind = async () => {
            // Only on partner street fields in forms
            try {
                const record = this.props?.record;
                if (!record) return; // not in form
                const isPartner = record.resModel === "res.partner";
                const isStreet = this.props?.name === "street";
                if (!isPartner || !isStreet) return;
                await loadGooglePlaces(this.rpc);
                if (!(window.google && window.google.maps && window.google.maps.places)) {
                    return;
                }
                const input = this.el?.querySelector?.("input, textarea");
                if (input) {
                    await attachPlacesAutocomplete(this, input);
                }
            } catch (e) {
                console.warn("GPlaces attach error", e);
            }
        };
        onMounted(bind);
        onPatched(bind);
    },
});

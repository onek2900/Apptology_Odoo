/** @odoo-module **/

import { registry } from "@web/core/registry";
import { CharField } from "@web/views/fields/char/char_field";
import { loadJS } from "@web/core/assets";
import { onMounted } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

let googleScriptLoading;

async function loadGooglePlaces(env, rpc) {
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
                "Google Places API key is not set. Go to Settings > Technical > Parameters or General Settings to configure it."
            );
            return;
        }
        const url = `https://maps.googleapis.com/maps/api/js?key=${encodeURIComponent(
            apiKey
        )}&libraries=places`;
        googleScriptLoading = loadJS(url).catch((e) => {
            console.error("Failed loading Google Maps script", e);
            googleScriptLoading = undefined;
        });
    }
    await googleScriptLoading;
}

export class GooglePlacesAddress extends CharField {
    setup() {
        super.setup();
        this.rpc = useService("rpc");
        onMounted(this._onMounted.bind(this));
    }

    async _onMounted() {
        await loadGooglePlaces(this.env, this.rpc);
        if (!(window.google && window.google.maps && window.google.maps.places)) {
            return;
        }
        // Ensure input exists
        const input = this.el.querySelector("input");
        if (!input) return;

        const autocomplete = new window.google.maps.places.Autocomplete(input, {
            types: ["geocode"],
            fields: [
                "address_components",
                "geometry",
                "formatted_address",
            ],
        });

        autocomplete.addListener("place_changed", async () => {
            const place = autocomplete.getPlace();
            if (!place || !place.address_components) {
                return;
            }
            const comp = {};
            for (const c of place.address_components) {
                for (const t of c.types) {
                    comp[t] = c;
                }
            }
            const values = {};
            // street number + route
            const streetNumber = comp["street_number"]?.long_name || "";
            const route = comp["route"]?.long_name || "";
            const street = [streetNumber, route].filter(Boolean).join(" ");
            if (street) values["street"] = street;
            if (comp["locality"]) values["city"] = comp["locality"].long_name;
            if (comp["postal_code"]) values["zip"] = comp["postal_code"].long_name;

            const canSet = (name) =>
                this.props.record && this.props.record.activeFields &&
                Object.prototype.hasOwnProperty.call(this.props.record.activeFields, name);
            if (place.geometry && place.geometry.location) {
                const loc = place.geometry.location;
                if (canSet("partner_latitude")) values["partner_latitude"] = loc.lat();
                if (canSet("partner_longitude")) values["partner_longitude"] = loc.lng();
            }

            // Country and state resolution via RPC
            const countryName = comp["country"]?.long_name;
            const countryCode = comp["country"]?.short_name;
            const stateName = comp["administrative_area_level_1"]?.long_name;
            const stateCode = comp["administrative_area_level_1"]?.short_name;

            try {
                if (countryName || countryCode) {
                    const countries = await this.rpc("/web/dataset/call_kw", {
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
                    const states = await this.rpc("/web/dataset/call_kw", {
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
                // Update the form record with derived values
                await this.props.record.update(values);
                // Put formatted address into this field (optional)
                const formatted = place.formatted_address || street;
                if (formatted) {
                    await this.props.update(formatted);
                }
            } catch (e) {
                console.error("Failed updating record from Places selection", e);
            }
        });
    }
}

GooglePlacesAddress.supportedTypes = ["char"];

registry.category("fields").add("google_places_address", GooglePlacesAddress);

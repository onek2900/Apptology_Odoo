{
    "name": "Apptology Address Autofill (Google Places)",
    "summary": "Auto-fill partner address using Google Places Autocomplete",
    "version": "17.0.1.0.0",
    "category": "Contacts",
    "author": "Apptology",
    "website": "",
    "license": "OPL-1",
    "depends": [
        "base",
        "web",
        "contacts",
    ],
    "data": [
        "views/res_partner_views.xml",
        "views/res_config_settings_simple.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "apptology_address_autofill/static/src/js/patch_char_field_gplaces.js",
            "apptology_address_autofill/static/src/css/gplaces.css",
        ],
    },
    "maintainers": ["apptology"],
    "application": False,
    "installable": True,
}

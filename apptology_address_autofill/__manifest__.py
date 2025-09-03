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
    ],
    "assets": {
        "web.assets_backend": [
            "apptology_address_autofill/static/src/js/google_places_widget.js",
        ],
    },
    "maintainers": ["apptology"],
    "application": False,
    "installable": True,
}

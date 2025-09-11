{
    "name": "Apptology Dashboard Extensions",
    "summary": "Adds Today, Yesterday, Specific Date to Spreadsheet Dashboard period selector",
    "version": "17.0.1.0.0",
    "author": "Apptology",
    "license": "LGPL-3",
    "depends": [
        "web",
        "spreadsheet_dashboard",
    ],
    "data": [],
    "assets": {
        "web.assets_backend": [
            "apptology_dashboard/static/src/js/period_presets_patch.js",
            "apptology_dashboard/static/src/js/specific_date_dialog.js",
        ],
    },
    "installable": True,
}

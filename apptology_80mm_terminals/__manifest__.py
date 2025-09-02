{
    "name": "Apptology 80mm Terminals (POS Receipt 80mm)",
    "author": "Apptology",
    "version": "17.0.1.0.0",
    "license": "OPL-1",
    "website": "https://apptology.sa/",
    "category": "Point of Sale",
    "summary": "Force POS receipt width to 80mm for thermal printers.",
    "description": """
    Enforces an 80mm receipt width in the POS UI and print.
    """,
    "depends": ["base", "point_of_sale", "pos_restaurant"],
    "data": [],
    "assets": {
        "point_of_sale._assets_pos": [
            "apptology_80mm_terminals/static/src/css/custom.css",
            "apptology_80mm_terminals/static/src/xml/pos_receipt.xml",
        ],
    },
    "images": [],
    "installable": true,
    "auto_install": false,
    "application": false
}


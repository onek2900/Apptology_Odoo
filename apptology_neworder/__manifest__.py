{
    "name": "Apptology POS New Order (Floor)",
    "summary": "Adds a New Order button on the floor plan to start pickup orders without a table.",
    "version": "17.0.1.0.0",
    "category": "Point of Sale",
    "author": "Apptology",
    "website": "https://apptology.com",
    "license": "OEEL-1",
    "depends": ["point_of_sale", "pos_restaurant"],
    "assets": {
        "point_of_sale._assets_pos": [
            "apptology_neworder/static/src/xml/floor_neworder_button.xml",
                        "apptology_neworder/static/src/scss/floor_neworder_button.scss"
        ]
    },
    "installable": True
}



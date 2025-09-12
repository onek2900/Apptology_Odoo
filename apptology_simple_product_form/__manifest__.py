{
    "name": "Apptology Simple Product Form",
    "summary": "Simplified one-page product form with toppings",
    "version": "17.0.1.0.0",
    "author": "Apptology",
    "license": "LGPL-3",
    "depends": [
        "product",
        "point_of_sale",
        "sh_pos_all_in_one_retail",
    ],
    "data": [
        "views/product_template_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "apptology_simple_product_form/static/src/css/simple_form.scss",
            "apptology_simple_product_form/static/src/js/modifier_groups_widget.js",
            "apptology_simple_product_form/static/src/xml/modifier_groups_widget.xml",
        ],
    },
    "application": False,
}

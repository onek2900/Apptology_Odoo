# -*- coding: utf-8 -*-

{
    'name': 'Apptology Customer Screen',
    'version': '17.0.1.0.0',
    'category': 'Point Of Sale',
    'summary': '',
    'description': '',
    'depends': ['pos_restaurant', 'web', 'bus'],
    'data': [
        "views/order_index.xml",
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'apptology_customer_screen/static/src/xml/customer_facing_button.xml',
            'apptology_customer_screen/static/src/js/orderwidget.js',
        ],
        'web.assets_backend': [
            'apptology_customer_screen/static/src/css/customer.scss',
            'apptology_customer_screen/static/src/js/custom_screen.js',
            'apptology_customer_screen/static/src/xml/customer_screen_templates.xml',
        ],
        'apptology_order_tracking.assets': [
            # Web helpers and core assets
            ("include", "web._assets_helpers"),
            ("include", "web._assets_backend_helpers"),
            ("include", "web._assets_primary_variables"),

            # Bootstrap core
            "web/static/src/scss/pre_variables.scss",
            "web/static/lib/bootstrap/scss/_functions.scss",
            "web/static/lib/bootstrap/scss/_variables.scss",
            ("include", "web._assets_bootstrap"),

            'web/static/src/libs/fontawesome/css/font-awesome.css',
            'web/static/lib/odoo_ui_icons/*',
            'web/static/src/webclient/navbar/navbar.scss',
            'web/static/src/scss/animation.scss',
            'web/static/src/scss/fontawesome_overridden.scss',
            'web/static/src/scss/mimetypes.scss',
            'web/static/src/scss/ui.scss',
            'web/static/src/views/fields/translation_dialog.scss',
            'web/static/src/legacy/scss/ui.scss',

            # Core web assets
            ('include', 'web._assets_core'),

            # Remove unnecessary components
            ("remove", "web/static/src/core/debug/**/*"),

            # UI components
            "web/static/lib/odoo_ui_icons/*",
            'web/static/src/legacy/scss/ui.scss',

            'bus/static/src/*.js',
            'bus/static/src/services/**/*.js',
            'bus/static/src/workers/websocket_worker.js',
            'bus/static/src/workers/websocket_worker_utils.js',
            "point_of_sale/static/src/utils.js",

            # Module specific assets

            'apptology_customer_screen/static/src/css/customer.scss',
            'apptology_customer_screen/static/src/js/custom_screen.js',
            'apptology_customer_screen/static/src/xml/customer_screen_templates.xml',

            'apptology_customer_screen/static/src/js/mountApps.js',
        ]
    },
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}

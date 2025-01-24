# -*- coding: utf-8 -*-

{
    'name': 'POS Kitchen Screen',
    'version': '17.0.1.0.0',
    'category': 'Point Of Sale',
    'summary': '',
    'description': '',
    'depends': ['pos_restaurant', 'web', 'bus'],
    'data': [
        "views/order_index.xml",
        'security/pos_kitchen_screen_groups.xml',
        "security/ir.model.access.csv",
        'data/kitchen_screen_sequence_data.xml',
        "views/kitchen_screen_views.xml",
        "views/pos_kitchen_screen_odoo_menus.xml",
        "views/pos_order_views.xml",
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_kitchen_screen_odoo/static/src/js/fields_load.js',
            'pos_kitchen_screen_odoo/static/src/js/order_payment.js',
            'pos_kitchen_screen_odoo/static/src/js/order_button.js',
        ],
        'web.assets_backend': [
            'pos_kitchen_screen_odoo/static/src/css/kitchen.scss',
            'pos_kitchen_screen_odoo/static/src/js/kitchen_screen.js',
            'pos_kitchen_screen_odoo/static/src/xml/kitchen_screen_templates.xml',
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
            'pos_kitchen_screen_odoo/static/src/css/order_screen.scss',
            'pos_kitchen_screen_odoo/static/src/xml/order_screen.xml',
            'pos_kitchen_screen_odoo/static/src/js/order_screen.js',

            'pos_kitchen_screen_odoo/static/src/css/kitchen.scss',
            'pos_kitchen_screen_odoo/static/src/js/kitchen_screen.js',
            'pos_kitchen_screen_odoo/static/src/xml/kitchen_screen_templates.xml',

            'pos_kitchen_screen_odoo/static/src/js/mountApps.js',
        ]
    },
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}

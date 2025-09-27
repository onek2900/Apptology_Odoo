# -*- coding: utf-8 -*-

{
    'name': 'POS Kitchen Screen',
    'version': '17.0.1.0.1',
    'category': 'Point Of Sale',
    'summary': '',
    'description': '',
    'depends': ['pos_restaurant', 'web', 'bus'],
    'data': [
        "security/ir.model.access.csv",
        "views/order_index.xml",
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
            'pos_kitchen_screen_odoo/static/src/js/navbar.js',
            'pos_kitchen_screen_odoo/static/src/xml/navbar.xml'
        ],
        # Load the standalone kitchen page via frontend assets instead of a custom bundle
        'web.assets_frontend': [
            # Ensure bus service is available on the standalone page
            'bus/static/src/*.js',
            'bus/static/src/services/**/*.js',
            'bus/static/src/workers/websocket_worker.js',
            'bus/static/src/workers/websocket_worker_utils.js',

            # Kitchen app assets
            'pos_kitchen_screen_odoo/static/src/css/kitchen.scss',
            'pos_kitchen_screen_odoo/static/src/js/kitchen_screen.js',
            'pos_kitchen_screen_odoo/static/src/xml/kitchen_screen_templates.xml',
            'pos_kitchen_screen_odoo/static/src/js/mountApps.js',
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}

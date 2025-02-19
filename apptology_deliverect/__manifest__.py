# -*- coding: utf-8 -*-

{
    'name': 'Apptology Deliverect',
    'version': '17.0.1.0.0',
    'category': 'Point Of Sale',
    'summary': '',
    'description': '',
    'depends': ['pos_restaurant', 'web', 'bus','pos_kitchen_screen_odoo'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/product_product_views.xml',
        'views/menu_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'apptology_deliverect/static/src/**/*',
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}

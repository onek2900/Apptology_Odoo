# -*- coding: utf-8 -*-

{
    'name': 'PoS Category Selection',
    'version': '1.0.0',
    'category': 'Sales/Point of Sale',
    'summary': 'PoS Category Selection',
    'depends': ['pos_restaurant'],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_category_selection/static/src/**/*',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}

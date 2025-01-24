# -*- coding: utf-8 -*-

{
    'name': 'Pos Nearpay Gateway',
    'version': '1.0.0',
    'category': 'Sales/Point of Sale',
    'summary': 'Pos Nearpay Gateway',
    'depends': ['point_of_sale', 'pos_nearpay_config'],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_nearpay/static/src/**/*'
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}

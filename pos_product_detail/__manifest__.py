# -*- coding: utf-8 -*-
{
    'name': 'Pos Product Detail',
    'version': '1.0.0',
    'category': 'Sales/Point of Sale',
    'summary': 'Pos Product Detail',
    'depends': ['point_of_sale'],
    'data': [
    ],
    'assets': {
        'point_of_sale.assets_prod': [
            'pos_product_detail/static/src/**/*'
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}

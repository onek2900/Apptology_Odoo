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
        # JS/CSS (runtime) assets for POS
        'point_of_sale.assets': [
            'pos_product_detail/static/src/**/*.js',
            'pos_product_detail/static/src/**/*.scss',
        ],
        'point_of_sale.assets_prod': [
            'pos_product_detail/static/src/**/*.js',
            'pos_product_detail/static/src/**/*.scss',
        ],
        # QWeb templates must be in the qweb bundle in Odoo 16
        'point_of_sale.assets_qweb': [
            'pos_product_detail/static/src/**/*.xml',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}

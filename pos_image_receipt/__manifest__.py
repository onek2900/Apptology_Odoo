# -*- coding: utf-8 -*-

{
    'name': 'PoS Reciept Image Download',
    'version': '1.0.0',
    'category': 'Sales/Point of Sale',
    'summary': 'PoS Reciept Image Download',
    'depends': ['point_of_sale'],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_image_receipt/static/lib/**/*',
            'pos_image_receipt/static/src/**/*',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}

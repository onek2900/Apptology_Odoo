# -*- coding: utf-8 -*-

{
    'name': 'Apptology Pos Moneris Terminal',
    'version': '17.0.1.0.0',
    'category': 'Sales/Point of Sale',
    'summary': 'Pos Moneris Terminal',
    'depends': ['point_of_sale'],
    'data': [
        "views/res_config_settings_views.xml",
        "views/pos_payment_method_views.xml",
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'apptology_pos_moneris/static/src/**/*'
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}

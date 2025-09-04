# -*- coding: utf-8 -*-

{
    'name': 'Apptology POS Address Autofill',
    'summary': 'Google Places autocomplete for customer address in POS',
    'version': '17.0.1.0.0',
    'category': 'Point of Sale',
    'depends': ['point_of_sale'],
    'data': [
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'apptology_address_autofill/static/src/js/pos_address_autocomplete.js',
            'apptology_address_autofill/static/src/xml/pos_address_autocomplete.xml',
        ],
    },
    'license': 'LGPL-3',
    'application': False,
    'installable': True,
}


# -*- coding: utf-8 -*-

{
    'name': 'Apptology Deliverect',
    'version': '17.0.1.0.0',
    'category': 'Point Of Sale',
    'summary': '',
    'description': '',
    'depends': ['pos_restaurant', 'web', 'bus'],
    'data': [
        'security/ir.model.access.csv',
        'views/deliverect_configuration_views.xml',
        'views/menu_views.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}

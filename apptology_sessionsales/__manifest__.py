# -*- coding: utf-8 -*-
{
    'name': 'Apptology Session Sales',
    'version': '17.0.1.0.0',
    'category': 'Point Of Sale',
    'summary': 'Print the closure report directly from the POS closing dialog.',
    'depends': ['point_of_sale'],
    'data': [],
    'assets': {
        'point_of_sale._assets_pos': [
            'apptology_sessionsales/static/src/js/close_pos_popup.js',
            'apptology_sessionsales/static/src/xml/close_pos_popup.xml',
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}

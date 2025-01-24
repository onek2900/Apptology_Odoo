# -*- coding: utf-8 -*-

{
    'name': 'Apptology Browsing',
    'version': '1.0.0',
    'category': 'Tools',
    'summary': 'Apptology Browsing',
    'depends': ['web'],
    'data': [
        'views/browsing_view.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'apptology_browsing/static/src/xml/browsing_action.xml',
            'apptology_browsing/static/src/js/browsing_action.js',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}

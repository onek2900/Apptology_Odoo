# -*- coding: utf-8 -*-

{
    'name': 'Apptology Google Sheet',
    'version': '1.0.0',
    'category': 'Tools',
    'summary': 'Import products from Google Sheets',
    'depends': ['base', 'product'],
    'data': [
        'views/res_config_settings_views.xml',
        'data/ir_cron_data.xml',
    ],
    'external_dependencies': {
        'python': ['google-auth', 'google-auth-oauthlib', 'google-auth-httplib2', 'google-api-python-client'],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}

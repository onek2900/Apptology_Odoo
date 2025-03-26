{
    'name': 'Custom Currency Riyal Symbol',
    'version': '1.0',
    'category': 'Localization',
    'summary': 'Add the new Riyal symbol to currencies in Odoo.',
    'license': 'AGPL-3',
    'depends': ['base'],
    'data': [
        'views/currency_riyal_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            '/custom_currency_riyal/static/src/css/currency_style.css',
        ],
    },
    'installable': True,
    'auto_install': False,
}

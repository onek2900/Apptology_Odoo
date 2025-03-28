# -*- coding: utf-8 -*-

{
    'name': "Main Server Data",
    'version': '17.0.1.0.0',
    'depends': ['base'],
    'author': "",
    'description': """
    Main server module for storing customer deliverect data
    """,
    'data': [
        'security/ir.model.access.csv',
        'views/main_server_data_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'auto_install': False,
}

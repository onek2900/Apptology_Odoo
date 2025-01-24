# -*- coding: utf-8 -*-

{
    'name': 'Apptology Pos Kitchen Printing',
    'version': '1.0.0',
    'category': 'Sales/Point of Sale',
    'summary': 'Apptology Pos Kitchen Printing',
    'depends': ['pos_restaurant'],
    'author': 'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'website': "https://www.cybrosys.com",
    'data': [
        'views/pos_printer_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
               'apptology_pos_kitchen_printing/static/src/js/**/*',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}

# -*- coding: utf-8 -*-
{
    'name': 'Apptology Pos Debranding',
    'version': '17.0.1.0.0',
    'category': '',
    'summary': '',
    "description": """""",
    'depends': [
        "point_of_sale",
    ],
    'data': [
        'views/pos.xml',
    ],
    "assets": {
        'point_of_sale._assets_pos': [
            'apptology_pos_debranding/static/src/xml/pos_branding.xml'
            'apptology_pos_debranding/static/src/xml/order_receipt.xml'
        ]
    },
    'installable': True,
    'auto_install': False,
}

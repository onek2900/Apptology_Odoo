# -*- coding: utf-8 -*-
{
    'name': 'Apptology Deliverect',
    'version': '17.0.1.0.0',
    'category': 'Point Of Sale',
    'summary': 'Module to Connect Deliverect with Odoo Point of Sale',
    'description': 'Module to Connect Deliverect with Odoo Point of Sale',
    'depends': ['account','point_of_sale','pos_restaurant','pos_kitchen_screen_odoo'],
    'data': [
        'security/ir.model.access.csv',
        # 'data/pos_payment_method_data.xml',
        'wizards/deliverect_info_wizard_views.xml',
        'views/res_config_settings_views.xml',
        'views/deliverect_modifier_group_views.xml',
        'views/product_product_views.xml',
        'views/point_of_sale_views.xml',
        'views/pos_payment_method_views.xml',
        'views/product_template_views.xml',
        'views/res_partner_views.xml',
        'views/menu_views.xml'
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'apptology_deliverect/static/src/**/*',
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
    'post_init_hook': 'post_init_hook',
}

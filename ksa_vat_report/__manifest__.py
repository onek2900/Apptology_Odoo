# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-
{
    'name': " ZATCA KSA VAT RETURN SUMMARY ",

     'summary': """
  KSA VAT Return form module is for Odoo users in Saudi Arabia for submitting VAT details in ZATCA portal .| Saudi VAT Return | It is a module which lookups on the invoices that is validated and posted. This brings you to identify the total consolidated VAT amount which is  posted on Odoo.
        
        """,

    'description': """
       It includes sales and purchase vat report based on tax grid configuration.Tax grid are automatically generated for sales and purchases.
       Also previous start is configured in settings.
    """,

    'author': "Loyal IT Solutions Pvt Ltd",
    'website': "https://www.loyalitsolutions.com/",
    'category': 'account',
    'version': '17.0.0.1',
    'license': 'AGPL-3',
    'price': '60.00',
    'currency': 'EUR',    
    'support': "support@loyalitsolutions.com",
    'depends': ['base', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'data/account_tag_data.xml',
        'views/ksa_vat_print.xml',
        'views/vat_report_menu.xml',
        'views/views.xml',
        'views/templates.xml',
        'wizard/ksa_vat_report_wizard.xml',
        'wizard/tax_grid_wizard_view.xml',

    ],
    'demo': [
        'demo/demo.xml',
    ],
   'images': ['static/description/VAT.gif'],
}

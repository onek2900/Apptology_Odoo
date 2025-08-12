{
    'name': 'POS Receipt VAT Summary',
    'summary': 'Adds a bilingual VAT (15%) line under TOTAL on POS receipts (display-only).',
    'version': '17.0.1.6.0',
    'author': 'Apptology Inc.',
    'website': 'https://apptologyinc.com',
    'license': 'LGPL-3',
    'category': 'Point of Sale',
    'depends': ['point_of_sale', 'l10n_gcc_pos'],
    'assets': {
        'point_of_sale.assets': [
            'pos_receipt_vat_summary/static/src/xml/receipt_vat_block.xml',
            'pos_receipt_vat_summary/static/src/xml/remove_gcc_line_tax.xml'
        ],
        'point_of_sale.assets_prod': [
            'pos_receipt_vat_summary/static/src/xml/receipt_vat_block.xml',
            'pos_receipt_vat_summary/static/src/xml/remove_gcc_line_tax.xml'
        ]
    },
    'installable': True,
    'application': False
}
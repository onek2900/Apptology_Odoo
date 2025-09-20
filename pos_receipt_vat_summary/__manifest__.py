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
        # Keep POS runtime bundles for backwards compatibility
        'point_of_sale.assets': [
            # no JS/SCSS here; XML belongs to qweb bundle
        ],
        'point_of_sale.assets_prod': [
            # no JS/SCSS here; XML belongs to qweb bundle
        ],
        # Ensure XML templates load in the POS QWeb bundle (Odoo 16)
        'point_of_sale.assets_qweb': [
            'pos_receipt_vat_summary/static/src/xml/receipt_vat_block.xml',
            'pos_receipt_vat_summary/static/src/xml/remove_gcc_line_tax.xml'
        ],
    },
    'installable': True,
    'application': False
}

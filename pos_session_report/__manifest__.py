{
    'name': 'POS Session Report Button',
    'version': '1.0',
    'summary': 'Add a button to display the Sale Details report when closing a POS session',
    'description': 'This module adds a button to the POS session closing wizard to display the Sale Details report.',
    'category': 'Point of Sale',
    'depends': ['point_of_sale'],
    'data': [
        'views/pos_session_views.xml',
    ],
    'installable': True,
    'application': False,
}
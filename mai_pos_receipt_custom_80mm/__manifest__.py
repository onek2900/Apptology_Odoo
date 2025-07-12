{
    "name" : "POS Custom Receipt- Thermal Print width of 80mm",
    "author" : "MAISOLUTIONSLLC",
    'sequence': 1,
    "version":"17.0.3.2.1",
    "license": 'OPL-1',    
    "price": 18,
    "currency": "EUR" ,
    "email": 'apps@maisolutionsllc.com',
    "website":'http://maisolutionsllc.com/',
    "category": "Point of Sale",
    "summary": "Using this module you can print Customised POS Receipt of width 80mm",
    "description": """
    Using this module you can print Customised POS Receipt of width 80mm.
    """,   
    "depends" : ['base','point_of_sale','pos_restaurant'],
    "data" : [
            ], 
    'assets': {
        'point_of_sale._assets_pos': [
            '/mai_pos_receipt_custom_80mm/static/src/css/custom.css'

        ],
    },
    'images': ['static/description/main_screenshot.gif'],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}

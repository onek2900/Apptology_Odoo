# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.
# Part of Softhealer Technologies.

{
    "name": "POS All In One Retail Shop and Restaurant Management | All in POS Retail | All in One Restaurant",

    "author": "Softhealer Technologies",  

    "website": "https://www.softhealer.com",   

    "support": "support@softhealer.com",   
     
    "category": "Point of Sale",   

    'version': '0.0.1',

    "summary": ""
    
    "license": "OPL-1",
    
    "depends": ['point_of_sale', 'pos_restaurant', 'pos_hr', 'sh_pos_all_in_one_retail'],

    "data": [],

    "assets": {
        'point_of_sale._assets_pos': [
            'sh_pos_all_in_one_restaurant/static/src/overrides/models/model.js',
        ],
    },

    "images": [
        'static/description/splash-screen.gif',
        'static/description/splash-screen_screenshot.gif'

    ],

    "auto_install": False,

    "application": True,

    "installable": True,

    "price": 8,

    "currency": "EUR"
}

# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.
{
    "name": "Point of Sale Retail Shop| POS Retail Shop| All In One POS Retail",         
    "author": "Softhealer Technologies",     
    "website": "https://www.softhealer.com",     
    "support": "support@softhealer.com",     
    "category": "Point of Sale",   
    "version": "0.0.10",       
    "summary": "",          
    "description": """ This is the fully retail solution for any kind of retail shop or bussiness.  """,
    "depends": ["point_of_sale", 'hr',"utm", "portal"],
    'external_dependencies': {
        'python': ['xlrd'],
    },
    "data": [
        'data/sh_pos_theme_responsive/data/pos_theme_settings_data.xml',
        
        'sh_pos_theme_responsive/security/ir.model.access.csv',
        'sh_pos_theme_responsive/views/sh_pos_theme_settings_views.xml',
        'data/order_label.xml',
        'data/cron_view.xml',
        'views/pos_order.xml',
        'views/res_config_settings.xml',
        'data/sh_pos_keayboard_shortcut/data/sh_keyboard_key_data.xml',
        'security/ir.model.access.csv',

        # varaint
        'sh_pos_product_variant/views/product_template.xml',

        # product suggtion
        'pos_product_suggestion/views/product_view.xml',

        'sh_pos_cash_in_out/views/cash_in_out_menu.xml',

        'sh_pos_product_toppings/views/pos_category_views.xml',
        'sh_pos_product_toppings/views/product_product_views.xml',
        'sh_pos_product_toppings/views/sh_product_toppings.xml',
        'sh_pos_product_toppings/views/sh_topping_group.xml',

        'sh_base_order_type/security/ir.model.access.csv',
        'sh_pos_order_type/views/sh_order_type_views.xml',
        'sh_pos_order_type/views/pos_order_views.xml',

        'sh_product_multi_barcode/security/ir.model.access.csv',
        'sh_product_multi_barcode/views/product_product_views.xml',
        'sh_product_multi_barcode/views/product_template_views.xml',
        'sh_product_multi_barcode/views/res_config_settings.xml',

        "sh_pos_reports/sh_pos_z_report/security/ir.model.access.csv",
        "sh_pos_reports/sh_pos_z_report/reports/pos_z_report_detail.xml",
        "sh_pos_reports/sh_pos_z_report/reports/report_zdetails.xml",
        "sh_pos_reports/sh_pos_z_report/views/pos_session_z_report.xml",
        "sh_pos_reports/sh_pos_z_report/views/pos_config_views.xml",
        "sh_pos_reports/sh_pos_z_report/wizard/pos_z_report_wizard.xml",
        "sh_pos_reports/sh_pos_z_report/views/res_users_views.xml",
        "sh_pos_reports/sh_pos_z_report/views/hr_employee_views.xml",

        'sh_pos_reports/sh_day_wise_pos/security/day_wise_report.xml',
        'sh_pos_reports/sh_day_wise_pos/security/ir.model.access.csv',
        'sh_pos_reports/sh_day_wise_pos/views/sh_day_wise_pos_views.xml',
        'sh_pos_reports/sh_day_wise_pos/wizard/sh_pos_order_report_views.xml',
        'sh_pos_reports/sh_day_wise_pos/report/sh_day_wise_pos_report_templates.xml',

        "sh_pos_reports/sh_payment_pos_report/security/sh_payment_pos_report_groups.xml",
        "sh_pos_reports/sh_payment_pos_report/security/ir.model.access.csv",
        "sh_pos_reports/sh_payment_pos_report/wizard/sh_pos_payment_report_wizard_views.xml",
        "sh_pos_reports/sh_payment_pos_report/report/sh_payment_pos_report_templates.xml",
        'sh_pos_reports/sh_payment_pos_report/views/sh_payment_report_views.xml',

        "sh_pos_reports/sh_pos_report_user/security/sh_pos_report_user.xml",
        "sh_pos_reports/sh_pos_report_user/security/ir.model.access.csv",
        "sh_pos_reports/sh_pos_report_user/wizard/sh_pos_report_user_wizard_views.xml",
        "sh_pos_reports/sh_pos_report_user/report/sh_pos_report_user_report_templates.xml",
        "sh_pos_reports/sh_pos_report_user/views/sh_pos_report_user_views.xml",

        "sh_pos_reports/sh_top_pos_customer/security/ir.model.access.csv",
        "sh_pos_reports/sh_top_pos_customer/wizard/sh_tc_pos_top_customer_wizard_views.xml",
        "sh_pos_reports/sh_top_pos_customer/report/sh_top_pos_customer_report_templates.xml",
        "sh_pos_reports/sh_top_pos_customer/views/sh_top_pos_customer_views.xml",

        "sh_pos_reports/sh_top_pos_product/security/ir.model.access.csv",
        "sh_pos_reports/sh_top_pos_product/wizard/sh_tsp_top_pos_product_wizard_views.xml",
        "sh_pos_reports/sh_top_pos_product/views/sh_tsp_top_pos_product_views.xml",
        "sh_pos_reports/sh_top_pos_product/report/top_pos_product_report.xml",

        "sh_pos_reports/sh_pos_profitability_report/security/sh_pos_profitibility_report_groups.xml",
        "sh_pos_reports/sh_pos_profitability_report/report/pos_order_line_views.xml",

        'sh_pos_reports/sh_customer_pos_analysis/security/ir.model.access.csv',
        'sh_pos_reports/sh_customer_pos_analysis/report/sh_customer_pos_analysis_report_templates.xml',
        'sh_pos_reports/sh_customer_pos_analysis/wizard/sh_pos_analysis_wizard_views.xml',
        'sh_pos_reports/sh_customer_pos_analysis/views/sh_customer_pos_analysis_views.xml',

        'sh_pos_reports/sh_pos_by_category/security/pos_by_category.xml',
        'sh_pos_reports/sh_pos_by_category/security/ir.model.access.csv',
        'sh_pos_reports/sh_pos_by_category/report/sh_pos_by_category_report_templates.xml',
        'sh_pos_reports/sh_pos_by_category/wizard/sh_pos_category_wizard_views.xml',
        'sh_pos_reports/sh_pos_by_category/views/sh_pos_by_product_category_views.xml',

        "sh_pos_reports/sh_pos_invoice_summary/security/ir.model.access.csv",
        "sh_pos_reports/sh_pos_invoice_summary/report/sh_pos_inv_summary_doc_report_templates.xml",
        "sh_pos_reports/sh_pos_invoice_summary/wizard/sh_pos_inv_summary_wizard_views.xml",
        "sh_pos_reports/sh_pos_invoice_summary/views/sh_pos_invoice_summary_views.xml",

        "sh_pos_reports/sh_pos_product_profit/security/ir.model.access.csv",
        "sh_pos_reports/sh_pos_product_profit/report/sh_pos_product_profit_doc_report_templates.xml",
        "sh_pos_reports/sh_pos_product_profit/wizard/sh_pos_product_profit_wizard_views.xml",
        "sh_pos_reports/sh_pos_product_profit/views/sh_pos_product_profit_views.xml",

        "sh_pos_reports/sh_product_pos_indent/security/ir.model.access.csv",
        "sh_pos_reports/sh_product_pos_indent/report/sh_pos_product_indent_doc_report_templates.xml",
        "sh_pos_reports/sh_product_pos_indent/wizard/sh_pos_product_indent_wizard_views.xml",
        "sh_pos_reports/sh_product_pos_indent/views/sh_product_pos_indent_views.xml",

        'sh_pos_reports/sh_pos_sector_report/security/ir.model.access.csv',
        'sh_pos_reports/sh_pos_sector_report/wizard/sh_pos_section_report_wizard_views.xml',
        'sh_pos_reports/sh_pos_sector_report/views/sh_pos_sector_views.xml',

        "sh_pos_chatter/security/sh_pos_chatter_groups.xml",
        "sh_pos_chatter/views/pos_order_views.xml",

        'sh_import_pos/security/import_pos_groups.xml',
        'sh_import_pos/security/ir.model.access.csv',
        'sh_import_pos/wizard/import_pos_wizard_views.xml',
        'sh_import_pos/views/pos_views.xml',

        'sh_pos_receipt/security/sh_pos_receipt_groups.xml',
        'sh_pos_receipt/report/pos_order_reports.xml',
        'sh_pos_receipt/data/mail_template_data.xml',
        'sh_pos_receipt/report/pos_order_templates.xml',
        'sh_pos_receipt/views/pos_order_views.xml',

        'sh_auto_validate_pos/views/log_track_view.xml',
        'sh_pos_direct_login/views/res_user_views.xml',

        "sh_message/security/ir.model.access.csv",
        "sh_message/wizard/sh_message_wizard.xml",

        'sh_pos_own_customers/views/res_partner_views.xml',

        'sh_pos_own_products/views/product_product_views.xml',

        'sh_pos_order_signature/views/pos_order_view.xml',

        'sh_pos_weight/views/pos_order_view.xml',
        'sh_pos_order_return_exchange/views/product_template.xml',

        'sh_pos_discount/security/ir.model.access.csv',
        'sh_pos_discount/views/pos_discount.xml',
        'sh_pos_discount/views/pos_order_views.xml',
        'sh_pos_access_rights/security/sh_pos_access_rights_groups.xml',
        'sh_pos_customer_maximum_discount/views/res_partner_views.xml',

        #portal pos
        'sh_portal_pos/security/ir.model.access.csv',
        'sh_portal_pos/views/pos_order_templates.xml',

        'sh_pos_product_template/security/ir.model.access.csv',
        'sh_pos_product_template/views/pos_template_product.xml',

        'sh_pos_advance_cache/security/ir.model.access.csv',

        "sh_pos_secondary/views/pos_order.xml",

        "sh_product_secondary/security/sh_product_secondary_unit_groups.xml",
        "sh_product_secondary/views/product_product_views.xml",
        "sh_product_secondary/views/product_template_views.xml",
        "sh_product_secondary/views/stock_quant_views.xml",
        
        # pos note
        'sh_pos_note/security/ir.model.access.csv',
        'sh_pos_note/views/pos_order.xml',
        'sh_pos_note/views/pre_define_note.xml',
        
        # Whatsapp Intergration
        'sh_pos_whatsapp_integration/views/res_users.xml',
    ],
    'assets': {
            'web.assets_backend': [
                'sh_pos_all_in_one_retail/static/sh_pos_advance_cache/static/src/app/indexDB.js',
                'sh_pos_all_in_one_retail/static/sh_pos_advance_cache/static/src/app/systray_activity_menu.js',
                'sh_pos_all_in_one_retail/static/sh_pos_advance_cache/static/src/xml/ShAdvanceCatchNotifications.xml',
            ],
            'point_of_sale._assets_pos': [
            # theme
            '/sh_pos_all_in_one_retail/static/sh_pos_theme_responsive/static/src/overrides/pos_theme_variables.scss',
            'sh_pos_all_in_one_retail/static/sh_pos_theme_responsive/static/src/scss/mixin.scss',
            'sh_pos_all_in_one_retail/static/sh_pos_theme_responsive/static/src/scss/theme_style_4.scss',
            'sh_pos_all_in_one_retail/static/sh_pos_theme_responsive/static/lib/owl.carousel.js',
            'sh_pos_all_in_one_retail/static/sh_pos_theme_responsive/static/lib/owl.carousel.css',
            'sh_pos_all_in_one_retail/static/sh_pos_theme_responsive/static/lib/owl.theme.default.min.css',
            'sh_pos_all_in_one_retail/static/sh_pos_theme_responsive/static/src/overrides/**/*',
            'sh_pos_all_in_one_retail/static/sh_pos_theme_responsive/static/src/scss/**/*',

            # pos counter
            'sh_pos_all_in_one_retail/static/sh_pos_counter/**/*',

            # create sale order from pos
            'sh_pos_all_in_one_retail/static/sh_pos_create_so/static/src/**/*',

            # Create purchase order from pos
            'sh_pos_all_in_one_retail/static/sh_pos_create_po/static/src/**/*',

            # pos order label
            'sh_pos_all_in_one_retail/static/sh_pos_order_label/static/src/**/*',

            # order list
            'sh_pos_all_in_one_retail/static/sh_pos_order_list/static/**/*',

            # Global pos models
            'sh_pos_all_in_one_retail/static/global_models/static/src/override/pos_store.js',
            
            # receipt extend
            'sh_pos_all_in_one_retail/static/sh_pos_receipt_extend/static/src/**/*',

            # variant merge
            'sh_pos_all_in_one_retail/static/sh_pos_product_variant/static/src/**/*',

            # Wh stock
            'sh_pos_all_in_one_retail/static/sh_pos_wh_stock/static/src/app/**/*',
            'sh_pos_all_in_one_retail/static/sh_pos_wh_stock/static/src/scss/**/*',

            # remove cart item
            'sh_pos_all_in_one_retail/static/sh_pos_remove_cart_item/static/src/**/*',

            # keayboard
            'sh_pos_all_in_one_retail/static/sh_pos_keyboard_shortcut/static/src/**/*',  

            # discount
            'sh_pos_all_in_one_retail/static/sh_pos_order_discount/static/src/**/*',

            # suggestion
            'sh_pos_all_in_one_retail/static/pos_product_suggestion/static/src/**/*',

            'sh_pos_all_in_one_retail/static/sh_pos_product_code/static/src/**/*',

            'sh_pos_all_in_one_retail/static/sh_pos_cash_in_out/static/src/**/*',

            'sh_pos_all_in_one_retail/static/sh_pos_product_toppings/static/src/app/**/*',
            'sh_pos_all_in_one_retail/static/sh_pos_product_toppings/static/src/overrides/components/product_screen/product_screen.js',
            'sh_pos_all_in_one_retail/static/sh_pos_product_toppings/static/src/overrides/models/pos_store.js',
            'sh_pos_all_in_one_retail/static/sh_pos_product_toppings/static/src/overrides/models/models.js',
            'sh_pos_all_in_one_retail/static/sh_pos_product_toppings/static/src/overrides/orderline/orderline.js',
            'sh_pos_all_in_one_retail/static/sh_pos_product_toppings/static/src/overrides/orderline/orderline.scss',
            'sh_pos_all_in_one_retail/static/sh_pos_product_toppings/static/src/overrides/orderline/orderline.xml',

            'sh_pos_all_in_one_retail/static/sh_pos_order_type/static/**/*',
            'sh_pos_all_in_one_retail/static/sh_pos_multi_barcode/static/src/overrides/**/*',

            #pos report
            'sh_pos_all_in_one_retail/static/sh_pos_reports/sh_pos_z_report/static/src/app/**/*',
            'sh_pos_all_in_one_retail/static/sh_pos_reports/sh_pos_z_report/static/src/overrides/**/*',

            # direct login
            'sh_pos_all_in_one_retail/static/sh_pos_direct_login/static/**/*',

            # own customer
            'sh_pos_all_in_one_retail/static/sh_pos_own_customers/static/**/*',

            # own products
            'sh_pos_all_in_one_retail/static/sh_pos_own_products/static/**/*',

            # default customer
            'sh_pos_all_in_one_retail/static/sh_pos_default_customer/static/**/*',

            # default invoice
            'sh_pos_all_in_one_retail/static/sh_pos_default_invoice/static/**/*',

            # order signature
            'web/static/lib/jSignature/jSignatureCustom.js',
            'web/static/src/libs/jSignatureCustom.js',
            'sh_pos_all_in_one_retail/static/sh_pos_order_signature/static/**/*',

            # auto lock
            'sh_pos_all_in_one_retail/static/sh_pos_auto_lock/static/**/*',

            # pos weight 
            'sh_pos_all_in_one_retail/static/sh_pos_weight/static/src/overrides/**/*',
            "sh_pos_all_in_one_retail/static/sh_pos_weight/static/src/scss/pos.scss",

            #line pricelist
            "sh_pos_all_in_one_retail/static/sh_pos_line_pricelist/static/src/overrides/models/pos_store.js",
            "sh_pos_all_in_one_retail/static/sh_pos_line_pricelist/static/src/overrides/models/model.js",
            "sh_pos_all_in_one_retail/static/sh_pos_line_pricelist/static/src/overrides/components/Orderline/orderline.xml",
            "sh_pos_all_in_one_retail/static/sh_pos_line_pricelist/static/src/overrides/components/Orderline/orderline.js",
            "sh_pos_all_in_one_retail/static/sh_pos_line_pricelist/static/src/apps/pricelist_popup/pricelist_popup.js",
            "sh_pos_all_in_one_retail/static/sh_pos_line_pricelist/static/src/apps/pricelist_popup/pricelist_popup.xml",
            "sh_pos_all_in_one_retail/static/sh_pos_line_pricelist/static/src/overrides/components/product_screen/product_screen.js",
            "sh_pos_all_in_one_retail/static/sh_pos_line_pricelist/static/src/scss/pos.scss",

            #return exchange
            'sh_pos_all_in_one_retail/static/sh_pos_order_return_exchange/static/src/apps/overrides/**/*',
            'sh_pos_all_in_one_retail/static/sh_pos_order_return_exchange/static/src/apps/screens/**/*',
            'sh_pos_all_in_one_retail/static/sh_pos_order_return_exchange/static/src/apps/popups/**/*',

            #pos discount
            'sh_pos_all_in_one_retail/static/sh_pos_discount/static/src/app/popup/discount_popup/discount_popup.js',
            'sh_pos_all_in_one_retail/static/sh_pos_discount/static/src/app/popup/discount_popup/discount_popup.xml',
            'sh_pos_all_in_one_retail/static/sh_pos_discount/static/src/app/popup/discount_popup/discount_popup.scss',
            'sh_pos_all_in_one_retail/static/sh_pos_discount/static/src/overrides/components/order_line/Orderline.xml',
            'sh_pos_all_in_one_retail/static/sh_pos_discount/static/src/overrides/models/models.js',
            'sh_pos_all_in_one_retail/static/sh_pos_discount/static/src/overrides/models/pos_store.js',

            # Access Rights
            'sh_pos_all_in_one_retail/static/sh_pos_access_rights/static/src/**/*',
            # 'sh_pos_all_in_one_retail/static/sh_pos_access_rights/static/src/overrides/components/payment_screen/payment_screen.xml',

            #product template
            "sh_pos_all_in_one_retail/static/sh_pos_product_template/static/src/**/*",

            #customer maximum discount
            'sh_pos_all_in_one_retail/static/sh_pos_customer_maximum_discount/static/src/scss/**/*.scss',
            'sh_pos_all_in_one_retail/static/sh_pos_customer_maximum_discount/static/src/**/*',

            #advance cache
            'sh_pos_all_in_one_retail/static/sh_pos_advance_cache/static/src/app/indexDB.js',
            'sh_pos_all_in_one_retail/static/sh_pos_advance_cache/static/src/js/cache_customer.js',
            'sh_pos_all_in_one_retail/static/sh_pos_advance_cache/static/src/js/cache_product.js',
            'sh_pos_all_in_one_retail/static/sh_pos_advance_cache/static/src/js/chrome.js',

            #pos secondary
            'sh_pos_all_in_one_retail/static/sh_pos_secondary/static/src/apps/control_buttons/change_UOM_button/change_UOM_button.js',
            'sh_pos_all_in_one_retail/static/sh_pos_secondary/static/src/apps/control_buttons/change_UOM_button/change_UOM_button.xml',
            'sh_pos_all_in_one_retail/static/sh_pos_secondary/static/src/overrides/models/models.js',
            'sh_pos_all_in_one_retail/static/sh_pos_secondary/static/src/overrides/components/order_line/order_line.xml',
            "sh_pos_all_in_one_retail/static/sh_pos_secondary/static/src/overrides/components/ticket_screen/ticket_screen.js",
            
            # Return Exchange Barcode
            'sh_pos_all_in_one_retail/static/sh_pos_order_return_exchange_barcode/static/src/apps/models.js',
            'sh_pos_all_in_one_retail/static/sh_pos_order_return_exchange_barcode/static/src/overrides/popups/return_order_popup/return_order_popup.js',
            'sh_pos_all_in_one_retail/static/sh_pos_order_return_exchange_barcode/static/src/overrides/screens/PaymentScreen.js',
            'sh_pos_all_in_one_retail/static/sh_pos_order_return_exchange_barcode/static/src/overrides/screens/product_screen.js',
            'sh_pos_all_in_one_retail/static/sh_pos_order_return_exchange_barcode/static/src/xml/pos.xml',
            'sh_pos_all_in_one_retail/static/sh_pos_order_return_exchange_barcode/static/src/scss/pos_order_return_exchange.scss',
            'sh_pos_all_in_one_retail/static/sh_pos_order_return_exchange_barcode/static/src/scss/pos.scss',
            
            # POS Note
            'sh_pos_all_in_one_retail/static/sh_pos_note/static/src/**/*',
            
            # Whatsapp Intergration
            'sh_pos_all_in_one_retail/static/sh_pos_whatsapp_integration/static/src/**/*',
        ]
    },
    "images": [
        'static/description/splash-screen.gif',
        'static/description/splash-screen_screenshot.gif'

    ],
    "application": True,
    "auto_install": False,
    "license": "OPL-1",
    "price": 182.58,
    "currency": "EUR",
    "installable": True,
}

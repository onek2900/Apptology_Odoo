# -*- coding: utf-8 -*-
{
    'name': 'Apptology Debranding',
    'version': '17.0.1.0.0',
    'category': '',
    'summary': '',
    "description": """""",
    'depends': [
        "base_setup",
        "mail_bot",
        'web_editor'
    ],
    'data': [
        "data/data.xml",
        "views/login_layout.xml",
        "views/res_config_settings.xml",
    ],
    "assets": {
        "web.assets_backend": [
            'apptology_debranding/static/src/js/**/*',
        ],
        'web_editor.backend_assets_wysiwyg': [
            'apptology_debranding/static/src/xml/*',
        ],

    },
    "external_dependencies": {"python": ["lxml"]},
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

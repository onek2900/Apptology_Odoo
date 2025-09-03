# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request


class AddressAutofillController(http.Controller):
    @http.route('/apptology_address_autofill/places_key', type='json', auth='user')
    def get_places_key(self):
        enabled = request.env['ir.config_parameter'].sudo().get_param(
            'apptology_address_autofill.google_places_enabled', default='False'
        )
        if str(enabled).lower() not in ('1', 'true', 'yes'):
            return {'enabled': False, 'api_key': ''}
        key = request.env['ir.config_parameter'].sudo().get_param(
            'apptology_address_autofill.google_places_api_key', default=''
        )
        return {'enabled': True, 'api_key': key or ''}


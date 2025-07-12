# -*- coding: utf-8 -*-
# from odoo import http


# class KsaVatReport(http.Controller):
#     @http.route('/ksa_vat_report/ksa_vat_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ksa_vat_report/ksa_vat_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('ksa_vat_report.listing', {
#             'root': '/ksa_vat_report/ksa_vat_report',
#             'objects': http.request.env['ksa_vat_report.ksa_vat_report'].search([]),
#         })

#     @http.route('/ksa_vat_report/ksa_vat_report/objects/<model("ksa_vat_report.ksa_vat_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ksa_vat_report.object', {
#             'object': obj
#         })

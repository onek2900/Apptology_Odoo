# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api, _


class SaleConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    gen_barcode = fields.Boolean("On Product create generate Barcode EAN13")
    generate_option = fields.Selection([('date', 'On Product create generate Barcode EAN13 (Using Today Date)'),
                                        ('random', 'On Product create generate Barcode EAN13 (Using Random Number)')],string='Barcode Generate Option',default='date')

    

    def get_values(self):
        res = super(SaleConfigSettings, self).get_values()
        gen_barcode = self.env['ir.config_parameter'].sudo().get_param('bi_generate_product_ean13.gen_barcode')
        generate_option= self.env['ir.config_parameter'].sudo().get_param('bi_generate_product_ean13.generate_option')
        res.update(
            gen_barcode = gen_barcode,
            generate_option = generate_option
        )
        return res

    def set_values(self):
        super(SaleConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('bi_generate_product_ean13.gen_barcode', self.gen_barcode)
        self.env['ir.config_parameter'].sudo().set_param('bi_generate_product_ean13.generate_option', self.generate_option)
        

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

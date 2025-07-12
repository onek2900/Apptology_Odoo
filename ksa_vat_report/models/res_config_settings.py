
from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    vat_report_previous_start_date = fields.Date(string="VAT Report Previous Start Date")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        vat_report_previous_start_date = params.get_param('ksa_vat_report.vat_report_previous_start_date',
                                                 default=False)
        res.update(vat_report_previous_start_date=vat_report_previous_start_date)
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param("ksa_vat_report.vat_report_previous_start_date",
                                                         self.vat_report_previous_start_date)


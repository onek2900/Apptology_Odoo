from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import UserError
from datetime import datetime,timedelta

class VATReport(models.TransientModel):
    """ KSA Vat Report Wizard """
    _name = "ksa.vat.report"
    _description = "KSA VAT REPORT"


    date_from=fields.Date(string='Start Date', default=date.today(),required=True)
    date_to=fields.Date(string='End Date', default=date.today(),required=True)
    company_id = fields.Many2one('res.company',string='Company Name', required=True)



    def _build_contexts(self, data):
        result = {}

        result['date_from'] = data['form']['date_from'] or False
        result['date_to'] = data['form']['date_to'] or False
        # result['strict_range'] = True if result['date_from'] else False
        return result


    def vat_report_print (self):
        self.ensure_one()
        if not self.date_from:
            raise UserError(_("You must choose a Start Date"))
        vat_report_previous_start_date = (self.env['ir.config_parameter'].sudo().get_param(
            "ksa_vat_report.vat_report_previous_start_date"))

        vat_report_previous_start_date_temp = datetime.strptime(vat_report_previous_start_date, '%Y-%m-%d').date()


        if self.date_from<=vat_report_previous_start_date_temp:
            raise UserError(_("The date doesn't match the time period."))
        if self.date_from>self.date_to:
            raise UserError(_("The date must fall inside the specified time frame."))


        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(
            ['date_from', 'date_to', 'company_id'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context,
                                            lang=self.env.context.get(
                                                'lang') or 'en_US')
        return self.env.ref(
            'ksa_vat_report.ksa_vat_report_print_menu').report_action(self,
                                                                         data=data)
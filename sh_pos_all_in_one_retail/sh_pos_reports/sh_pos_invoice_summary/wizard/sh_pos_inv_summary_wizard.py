# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from base64 import encodebytes
from datetime import datetime
from io import BytesIO
from pytz import utc, timezone
from xlwt import Workbook, easyxf
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT


class POSInvoiceSummaryWizard(models.TransientModel):
    _name = 'sh.pos.inv.summary.wizard'
    _description = 'POS Invoice Summary Wizard'

    sh_start_date = fields.Datetime(
        'Start Date', required=True, default=fields.Datetime.now)
    sh_end_date = fields.Datetime(
        'End Date', required=True, default=fields.Datetime.now)
    sh_partner_ids = fields.Many2many(
        'res.partner', string='Customers', required=True)
    sh_session_id = fields.Many2one('pos.session', 'Session')
    sh_status = fields.Selection(
        [('both', 'Both'), ('open', 'Open'), ('paid', 'Paid')], string="Status", default='both')
    company_ids = fields.Many2many(
        'res.company', default=lambda self: self.env.companies, string="Companies")

    @api.constrains('sh_start_date', 'sh_end_date')
    def _check_dates(self):
        if self.filtered(lambda c: c.sh_end_date and c.sh_start_date > c.sh_end_date):
            raise ValidationError(_('start date must be less than end date.'))

    def print_report(self):
        datas = self.read()[0]
        return self.env.ref('sh_pos_all_in_one_retail.sh_pos_inv_summary_action').report_action([], data=datas)

    def display_report(self):
        datas = self.read()[0]
        report = self.env['report.sh_pos_all_in_one_retail.sh_pos_inv_summary_doc']
        data_values = report._get_report_values(
            docids=None, data=datas).get('customer_order_dic')

        if data_values:
            self.env['sh.pos.invoice.summary'].search([]).unlink()
            for customer in data_values:
                for order in data_values[customer]:
                    self.env['sh.pos.invoice.summary'].create({
                        'sh_partner_id': order['partner_id'],
                        'name': order['order_number'],
                        'order_date': order['order_date'],
                        'invoice_number': order['invoice_number'],
                        'invoice_date': order['invoice_date'],
                        'amount_invoiced': order['invoice_amount'],
                        'amount_paid': order['invoice_paid_amount'],
                        'amount_due': order['due_amount']
                    })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Point Of Sale Invoice Summary',
            'view_mode': 'tree',
            'res_model': 'sh.pos.invoice.summary',
            'context': "{'create': False,'search_default_group_customer': 1}"
        }

    def print_xls_report(self):
        workbook = Workbook(encoding='utf-8')
        heading_format = easyxf(
            'font:height 300,bold True;pattern: pattern solid, fore_colour gray25;align: horiz center')
        bold = easyxf(
            'font:bold True,height 215;pattern: pattern solid, fore_colour gray25;align: horiz center')
        bold_center = easyxf(
            'font:height 240,bold True;pattern: pattern solid, fore_colour gray25;align: horiz center;')
        worksheet = workbook.add_sheet(
            'Point Of Sale Invoice Summary', bold_center)
        worksheet.write_merge(
            0, 1, 0, 6, 'Point Of Sale Invoice Summary', heading_format)
        left = easyxf('align: horiz center;font:bold True')
        center = easyxf('align: horiz center;')
        bold_center_total = easyxf('align: horiz center;font:bold True')

        user_tz = self.env.user.tz or utc
        local = timezone(user_tz)
        start_date = datetime.strftime(utc.localize(datetime.strptime(str(
            self.sh_start_date), DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local), DEFAULT_SERVER_DATETIME_FORMAT)
        end_date = datetime.strftime(utc.localize(datetime.strptime(str(
            self.sh_end_date), DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local), DEFAULT_SERVER_DATETIME_FORMAT)
        worksheet.write_merge(2, 2, 0, 6, start_date + " to " + end_date, bold)
        worksheet.col(0).width = int(25 * 260)
        worksheet.col(1).width = int(25 * 260)
        worksheet.col(2).width = int(25 * 260)
        worksheet.col(3).width = int(25 * 260)
        worksheet.col(4).width = int(25 * 260)
        worksheet.col(5).width = int(25 * 260)
        worksheet.col(6).width = int(25 * 260)

        datas = self.read()[0]
        report = self.env['report.sh_pos_all_in_one_retail.sh_pos_inv_summary_doc']
        customer_order_dic = report._get_report_values(
            docids=None, data=datas).get('customer_order_dic')

        row = 4
        if customer_order_dic:
            for key in customer_order_dic.keys():
                worksheet.write_merge(
                    row, row, 0, 6, key, bold_center)
                row = row + 2
                total_amount_invoiced = 0.0
                total_amount_paid = 0.0
                total_amount_due = 0.0
                worksheet.write(row, 0, "Order Number", bold)
                worksheet.write(row, 1, "Order Date", bold)
                worksheet.write(row, 2, "Invoice Number", bold)
                worksheet.write(row, 3, "Invoice Date", bold)
                worksheet.write(row, 4, "Amount Invoiced", bold)
                worksheet.write(row, 5, "Amount Paid", bold)
                worksheet.write(row, 6, "Amount Due", bold)
                row = row + 1
                for rec in customer_order_dic[key]:
                    worksheet.write(row, 0, rec.get('order_number'), center)
                    worksheet.write(row, 1, str(rec.get('order_date')), center)
                    worksheet.write(row, 2, rec.get('invoice_number'), center)
                    worksheet.write(row, 3, str(
                        rec.get('invoice_date')), center)
                    worksheet.write(row, 4, str(rec.get(
                        'invoice_currency_symbol'))+str("{:.2f}".format(rec.get('invoice_amount'))), center)
                    worksheet.write(row, 5, str(rec.get(
                        'invoice_currency_symbol'))+str("{:.2f}".format(rec.get('invoice_paid_amount'))), center)
                    worksheet.write(row, 6, str(rec.get(
                        'invoice_currency_symbol'))+str("{:.2f}".format(rec.get('due_amount'))), center)
                    total_amount_invoiced = float(total_amount_invoiced) + \
                        rec.get('invoice_amount')
                    total_amount_paid = float(total_amount_paid) + \
                        rec.get('invoice_paid_amount')
                    total_amount_due = float(
                        total_amount_due) + rec.get('due_amount')
                    row = row + 1
                worksheet.write(row, 3, "Total", left)
                worksheet.write(row, 4, "{:.2f}".format(
                    total_amount_invoiced), bold_center_total)
                worksheet.write(row, 5, "{:.2f}".format(
                    total_amount_paid), bold_center_total)
                worksheet.write(row, 6, "{:.2f}".format(
                    total_amount_due), bold_center_total)
                row = row + 2

        filename = 'Point Of Sale Invoice Summary.xls'
        fp = BytesIO()
        workbook.save(fp)
        data = encodebytes(fp.getvalue())
        ir_attachment = self.env['ir.attachment']
        attachment_vals = {
            "name": filename,
            "res_model": "ir.ui.view",
            "type": "binary",
            "datas": data,
            "public": True,
        }
        fp.close()

        attachment = ir_attachment.search([('name', '=', filename),
                                          ('type', '=', 'binary'),
                                          ('res_model', '=', 'ir.ui.view')],
                                         limit=1)
        if attachment:
            attachment.write(attachment_vals)
        else:
            attachment = ir_attachment.create(attachment_vals)

        url = "/web/content/" + \
            str(attachment.id) + "?download=true"
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }

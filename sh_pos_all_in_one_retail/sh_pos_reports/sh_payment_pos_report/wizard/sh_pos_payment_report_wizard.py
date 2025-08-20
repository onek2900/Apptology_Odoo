# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from base64 import encodebytes
from datetime import datetime, timedelta
from io import BytesIO
from pytz import utc, timezone
from xlwt import Workbook, easyxf
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT


class ShPaymentPosReportWizard(models.TransientModel):
    _name = "sh.pos.payment.report.wizard"
    _description = 'pos payment report wizard Model'

    @api.model
    def default_company_ids(self):
        is_allowed_companies = self.env.context.get(
            'allowed_company_ids', False)
        if is_allowed_companies:
            return is_allowed_companies
        return False

    date_start = fields.Datetime(
        string="Start Date", required=True, default=fields.Datetime.now)
    date_end = fields.Datetime(
        string="End Date", required=True, default=fields.Datetime.now)
    state = fields.Selection([
        ('all', 'All'),
        ('open', 'Open'),
        ('paid', 'Paid'),
    ], string='Status', default='all',required=True)
    user_ids = fields.Many2many(
        comodel_name='res.users',
        relation='rel_sh_payment_pos_report_wizard_res_user',
        string='User')
    company_ids = fields.Many2many(
        'res.company', string='Companies', default=default_company_ids)
    config_ids = fields.Many2many('pos.config', string='POS Configuration',
                                  required=True, domain="[('company_id' , 'in',company_ids )]")
    filter_invoice_data = fields.Selection([('all', 'Both'), ('with_invoice', 'With Invoice'), (
        'wo_invoice', 'Without Invoice')], string='POS Payments Include', default='all')

    @api.model
    def default_get(self, fields):
        rec = super(ShPaymentPosReportWizard, self).default_get(fields)
        search_users = self.env["res.users"].search([
            ('id', '=', self.env.user.id),
        ], limit=1)
        if self.env.user.has_group('point_of_sale.group_pos_manager'):
            rec.update({
                "user_ids": [(6, 0, search_users.ids)],
            })
        else:
            rec.update({
                "user_ids": [(6, 0, [self.env.user.id])],
            })
        return rec

    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        if self.filtered(lambda c: c.date_end and c.date_start > c.date_end):
            raise ValidationError(_('start date must be less than end date.'))

    def print_report(self):
        datas = self.read()[0]
        return self.env.ref('sh_pos_all_in_one_retail.sh_payment_pos_report_action').report_action([], data=datas)

    def display_report(self):
        datas = self.read()[0]
        report = self.env['report.sh_pos_all_in_one_retail.sh_payment_pos_report_doc']
        data_values = report._get_report_values(
            docids=None, data=datas).get('user_data_dic')
        self.env['sh.payment.report'].search([]).unlink()
        vals = list(data_values.values())
        for val in vals:
            dict_val = list(val.values())
            if len(val) > 0:
                for v in dict_val[0]:
                    bank = v.get('Bank', 0)
                    cash = v.get('Cash', 0)
                    customer_account = v.get('Customer Account', 0)
                    self.env['sh.payment.report'].create({
                        'name': v['Invoice'],
                        'invoice_date': v['Invoice Date'],
                        'invoice_user_id': v['User_id'],
                        'sh_partner_id': v['Customer_id'],
                        'bank': bank,
                        'cash': cash,
                        'customer_account': customer_account,
                        'total': v['Total'],
                    })
        return {
            'type': 'ir.actions.act_window',
            'name': 'POS Payment Report',
            'view_mode': 'tree',
            'res_model': 'sh.payment.report',
            'context': "{'create': False,'search_default_group_user': 1}"
        }

    def print_xls_report(self):
        workbook = Workbook(encoding='utf-8')
        heading_format = easyxf(
            'font:height 300,bold True;pattern: pattern solid, fore_colour gray25;align: horiz center')
        bold = easyxf(
            'font:bold True,height 215;pattern: pattern solid, fore_colour gray25;align: horiz center')
        total_bold = easyxf('font:bold True')
        bold_center = easyxf(
            'font:height 240,bold True;pattern: pattern solid, fore_colour gray25;align: horiz center;')
        if self.date_start:
            date_start = fields.Datetime.from_string(self.date_start)
        else:
            # start by default today 00:00:00
            user_tz = timezone(self.env.context.get(
                'tz') or self.env.user.tz or 'UTC')
            today = user_tz.localize(fields.Datetime.from_string(
                fields.Date.context_today(self)))
            date_start = today.astimezone(timezone('UTC'))

        if self.date_end:
            date_stop = fields.Datetime.from_string(self.date_end)
            # avoid a date_stop smaller than date_start
            if date_stop < date_start:
                date_stop = date_start + timedelta(days=1, seconds=-1)
        else:
            # stop by default today 23:59:59
            date_stop = date_start + timedelta(days=1, seconds=-1)
        user_tz = self.env.user.tz or utc
        local = timezone(user_tz)
        start_date = datetime.strftime(utc.localize(datetime.strptime(str(
            self.date_start), DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local), DEFAULT_SERVER_DATETIME_FORMAT)
        end_date = datetime.strftime(utc.localize(datetime.strptime(str(
            self.date_end), DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local), DEFAULT_SERVER_DATETIME_FORMAT)
        worksheet = workbook.add_sheet('POS Payment Report', bold_center)
        worksheet.write_merge(0, 1, 0, 7, 'POS Payment Report' + (' (With Invoice)' if self.filter_invoice_data ==
                              'with_invoice' else '') + (' (Without Invoice)' if self.filter_invoice_data == 'wo_invoice' else ''), heading_format)
        worksheet.write_merge(2, 2, 0, 7, start_date + " to " + end_date, bold)
        account_payment_obj = self.env["pos.payment"]
        account_journal_obj = self.env["pos.payment.method"]
        currency = False
        j_refund = 0.0
        data = {}
        grand_journal_dic = {}
        user_data_dic = {}
        search_user = self.env['res.users'].sudo().search(
            [('id', 'in', self.user_ids.ids)])
        journal_domain = []
        if self.company_ids:
            journal_domain.append(('company_id', 'in', self.company_ids.ids))
        search_journals = account_journal_obj.sudo().search(journal_domain)
        final_col_list = ["Invoice", "Invoice Date", "User", "Customer"]
        final_total_col_list = []
        for journal in search_journals:
            if journal.name not in final_col_list:
                final_col_list.append(journal.name)
            if journal.name not in final_total_col_list:
                final_total_col_list.append(journal.name)
        final_col_list.append("Total")
        final_total_col_list.append("Total")
        for user_id in search_user:
            domain = [
                ("payment_date", ">=", fields.Datetime.to_string(date_start)),
                ("payment_date", "<=", fields.Datetime.to_string(date_stop)),
            ]
            if self.state:
                state = self.state
                if state == 'all':
                    domain.append(
                        ('pos_order_id.state', 'not in', ['cancel']))
                elif state == 'open':
                    domain.append(
                        ('pos_order_id.state', 'in', ['draft']))
                elif state == 'paid':
                    domain.append(
                        ('pos_order_id.state', 'in', ['paid']))
            domain.append(
                ("pos_order_id.user_id", "=", user_id.id))
            if self.company_ids:
                domain.append(('company_id', 'in', self.company_ids.ids))
            if self.config_ids:
                session_ids = self.env['pos.session'].sudo().search(
                    [('config_id', 'in', self.config_ids.ids)])
                domain.append(
                    ("pos_order_id.session_id", "in", session_ids.ids))
            payments = account_payment_obj.sudo().search(domain)
            invoice_pay_dic = {}
            if payments and search_journals:
                for journal in search_journals:
                    for journal_wise_payment in payments.filtered(lambda x: x.payment_method_id.id == journal.id):
                        if self.filter_invoice_data and self.filter_invoice_data == 'all':
                            if journal_wise_payment.pos_order_id.account_move:
                                for invoice in journal_wise_payment.pos_order_id.account_move:
                                    if not currency:
                                        currency = invoice.currency_id
                                    if invoice.move_type == "out_invoice":
                                        if invoice_pay_dic.get(invoice.name, False):
                                            pay_dic = invoice_pay_dic.get(
                                                invoice.name)
                                            total = pay_dic.get("Total")
                                            if pay_dic.get(journal.name, False):
                                                amount = pay_dic.get(
                                                    journal.name)
                                                total += journal_wise_payment.amount
                                                amount += journal_wise_payment.amount
                                                pay_dic.update(
                                                    {journal.name: amount, "Total": total})
                                            else:
                                                total += journal_wise_payment.amount
                                                pay_dic.update(
                                                    {journal.name: journal_wise_payment.amount, "Total": total})
                                            invoice_pay_dic.update(
                                                {invoice.name: pay_dic})
                                        else:
                                            invoice_pay_dic.update({invoice.name: {journal.name: journal_wise_payment.amount, "Total": journal_wise_payment.amount, "Invoice": invoice.name,
                                                                                   "Customer": invoice.partner_id.name if invoice.partner_id else "Walking Customer", "Invoice Date": str(invoice.invoice_date), "User": invoice.user_id.name if invoice.user_id else "", "style": ''}})
                                    if invoice.move_type == "out_refund":
                                        j_refund += journal_wise_payment.amount
                                        if invoice_pay_dic.get(invoice.name, False):
                                            pay_dic = invoice_pay_dic.get(
                                                invoice.name)
                                            total = pay_dic.get("Total")
                                            if pay_dic.get(journal.name, False):
                                                amount = pay_dic.get(
                                                    journal.name)
                                                total -= journal_wise_payment.amount
                                                amount -= journal_wise_payment.amount
                                                pay_dic.update(
                                                    {journal.name: amount, "Total": total})
                                            else:
                                                total -= journal_wise_payment.amount
                                                pay_dic.update(
                                                    {journal.name: -1 * (journal_wise_payment.amount), "Total": total})
                                            invoice_pay_dic.update(
                                                {invoice.name: pay_dic})
                                        else:
                                            invoice_pay_dic.update({invoice.name: {journal.name: -1 * (journal_wise_payment.amount), "Total": -1 * (journal_wise_payment.amount), "Invoice": invoice.name,
                                                                                   "Customer": invoice.partner_id.name if invoice.partner_id else "Walking Customer", "Invoice Date": str(invoice.invoice_date), "User": invoice.user_id.name if invoice.user_id else "", "style": ''}})
                            else:
                                if not currency:
                                    currency = journal_wise_payment.currency_id
                                if invoice_pay_dic.get(journal_wise_payment.pos_order_id.name, False):
                                    pay_dic = invoice_pay_dic.get(
                                        journal_wise_payment.pos_order_id.name)
                                    total = pay_dic.get("Total")
                                    if pay_dic.get(journal.name, False):
                                        amount = pay_dic.get(
                                            journal.name)
                                        total += journal_wise_payment.amount
                                        amount += journal_wise_payment.amount
                                        pay_dic.update(
                                            {journal.name: amount, "Total": total})
                                    else:
                                        total += journal_wise_payment.amount
                                        pay_dic.update(
                                            {journal.name: journal_wise_payment.amount, "Total": total})

                                    invoice_pay_dic.update(
                                        {journal_wise_payment.pos_order_id.name: pay_dic})
                                else:
                                    invoice_pay_dic.update({journal_wise_payment.pos_order_id.name: {journal.name: journal_wise_payment.amount, "Total": journal_wise_payment.amount, "Invoice": journal_wise_payment.pos_order_id.name,
                                                                                                     "Customer": journal_wise_payment.pos_order_id.partner_id.name if journal_wise_payment.pos_order_id.partner_id else "Walking Customer", "Invoice Date": str(journal_wise_payment.payment_date.date()), "User": journal_wise_payment.pos_order_id.user_id.name if journal_wise_payment.pos_order_id.user_id else "", "style": ''}})
                        elif self.filter_invoice_data and self.filter_invoice_data == 'with_invoice':
                            if journal_wise_payment.pos_order_id.account_move:
                                for invoice in journal_wise_payment.pos_order_id.account_move:
                                    if not currency:
                                        currency = invoice.currency_id
                                    if invoice.move_type == "out_invoice":
                                        if invoice_pay_dic.get(invoice.name, False):
                                            pay_dic = invoice_pay_dic.get(
                                                invoice.name)
                                            total = pay_dic.get("Total")
                                            if pay_dic.get(journal.name, False):
                                                amount = pay_dic.get(
                                                    journal.name)
                                                total += journal_wise_payment.amount
                                                amount += journal_wise_payment.amount
                                                pay_dic.update(
                                                    {journal.name: amount, "Total": total})
                                            else:
                                                total += journal_wise_payment.amount
                                                pay_dic.update(
                                                    {journal.name: journal_wise_payment.amount, "Total": total})
                                            invoice_pay_dic.update(
                                                {invoice.name: pay_dic})
                                        else:
                                            invoice_pay_dic.update({invoice.name: {journal.name: journal_wise_payment.amount, "Total": journal_wise_payment.amount, "Invoice": invoice.name,
                                                                                   "Customer": invoice.partner_id.name if invoice.partner_id else "Walking Customer", "Invoice Date": str(invoice.invoice_date), "User": invoice.user_id.name if invoice.user_id else "", "style": ''}})
                                    if invoice.move_type == "out_refund":
                                        j_refund += journal_wise_payment.amount
                                        if invoice_pay_dic.get(invoice.name, False):
                                            pay_dic = invoice_pay_dic.get(
                                                invoice.name)
                                            total = pay_dic.get("Total")
                                            if pay_dic.get(journal.name, False):
                                                amount = pay_dic.get(
                                                    journal.name)
                                                total -= journal_wise_payment.amount
                                                amount -= journal_wise_payment.amount
                                                pay_dic.update(
                                                    {journal.name: amount, "Total": total})
                                            else:
                                                total -= journal_wise_payment.amount
                                                pay_dic.update(
                                                    {journal.name: -1 * (journal_wise_payment.amount), "Total": total})
                                            invoice_pay_dic.update(
                                                {invoice.name: pay_dic})
                                        else:
                                            invoice_pay_dic.update({invoice.name: {journal.name: -1 * (journal_wise_payment.amount), "Total": -1 * (journal_wise_payment.amount), "Invoice": invoice.name,
                                                                                   "Customer": invoice.partner_id.name if invoice.partner_id else "Walking Customer", "Invoice Date": str(invoice.invoice_date), "User": invoice.user_id.name if invoice.user_id else "", "style": ''}})
                        elif self.filter_invoice_data and self.filter_invoice_data == 'wo_invoice':
                            if not currency:
                                currency = journal_wise_payment.currency_id
                            if invoice_pay_dic.get(journal_wise_payment.pos_order_id.name, False):
                                pay_dic = invoice_pay_dic.get(
                                    journal_wise_payment.pos_order_id.name)
                                total = pay_dic.get("Total")
                                if pay_dic.get(journal.name, False):
                                    amount = pay_dic.get(
                                        journal.name)
                                    total += journal_wise_payment.amount
                                    amount += journal_wise_payment.amount
                                    pay_dic.update(
                                        {journal.name: amount, "Total": total})
                                else:
                                    total += journal_wise_payment.amount
                                    pay_dic.update(
                                        {journal.name: journal_wise_payment.amount, "Total": total})

                                invoice_pay_dic.update(
                                    {journal_wise_payment.pos_order_id.name: pay_dic})
                            else:
                                if journal_wise_payment.pos_order_id.state != 'invoiced':
                                    invoice_pay_dic.update({journal_wise_payment.pos_order_id.name: {journal.name: journal_wise_payment.amount, "Total": journal_wise_payment.amount, "Invoice": journal_wise_payment.pos_order_id.name,
                                                                                                     "Customer": journal_wise_payment.pos_order_id.partner_id.name if journal_wise_payment.pos_order_id.partner_id else "Walking Customer", "Invoice Date": str(journal_wise_payment.payment_date.date()), "User": journal_wise_payment.pos_order_id.user_id.name if journal_wise_payment.pos_order_id.user_id else "", "style": ''}})
            final_list = []
            total_journal_amount = {}
            for key, value in invoice_pay_dic.items():
                final_list.append(value)
                for col_name in final_total_col_list:
                    if total_journal_amount.get(col_name, False):
                        total = total_journal_amount.get(col_name)
                        total += value.get(col_name, 0.0)

                        total_journal_amount.update({col_name: total})
                    else:
                        total_journal_amount.update(
                            {col_name: value.get(col_name, 0.0)})
            search_user = self.env['res.users'].sudo().search([
                ('id', '=', user_id.id)
            ], limit=1)
            if search_user and final_list and total_journal_amount:
                user_data_dic.update({
                    search_user.name: {'pay': final_list,
                                       'grand_total': total_journal_amount}
                })
            for col_name in final_total_col_list:
                j_total = 0.0
                j_total = total_journal_amount.get(col_name, 0.0)
                j_total += grand_journal_dic.get(col_name, 0.0)
                grand_journal_dic.update({col_name: j_total})
            j_refund = j_refund * -1
            grand_journal_dic.update({'Refund': j_refund})
        if user_data_dic:
            data.update({
                'columns': final_col_list,
                'user_data_dic': user_data_dic,
                'grand_journal_dic': grand_journal_dic,
            })
        else:
            raise UserError(_(
                'There is no Data Found between these dates...'))

        row = 3
        col = 0

        for user in user_data_dic.keys():
            pay_list = []
            pay_list.append(user_data_dic.get(user).get('pay', []))
            row = row + 2
            worksheet.write_merge(row, row, 0, 7, "User: " + user, bold_center)
            row = row + 2
            col = 0
            for column in data.get('columns'):
                worksheet.col(col).width = int(25 * 260)

                if column == "Invoice" and self.filter_invoice_data != "with_invoice":
                    worksheet.write(
                        row, col, ("Shop" if self.filter_invoice_data == "wo_invoice" else "Shop/Invoice"), bold)
                else:
                    worksheet.write(row, col, column, bold)
                col = col + 1
            for p in pay_list:
                row = row + 1
                col = 0
                for dic in p:
                    row = row + 1
                    col = 0
                    for column in data.get('columns'):
                        style = easyxf(dic.get('style', ''))
                        worksheet.write(row, col, dic.get(column, 0), style)
                        col = col + 1
            row = row + 1
            col = 3
            worksheet.col(col).width = int(25 * 260)
            worksheet.write(row, col, "Total", total_bold)
            col = col + 1
            if user_data_dic.get(user, False):
                grand_total = user_data_dic.get(user).get('grand_total', {})
                if grand_total:
                    for column in data.get('columns'):
                        if column not in ['Invoice', 'Invoice Date', 'User', 'Customer']:
                            worksheet.write(row, col, grand_total.get(
                                column, 0), total_bold)
                            col = col + 1
        row = row + 2
        worksheet.write_merge(row, row, 0, 1, "Payment Method", bold)
        row = row + 1
        worksheet.write(row, 0, "Name", bold)
        worksheet.write(row, 1, "Total", bold)
        for column in data.get('columns'):
            col = 0
            if column not in ["Invoice", "Invoice Date", "User", "Customer"]:
                row = row + 1
                worksheet.col(col).width = int(25 * 260)
                worksheet.write(row, col, column)
                col = col + 1
                worksheet.write(row, col, grand_journal_dic.get(column, 0))
        if grand_journal_dic.get('Refund', False):
            row = row + 1
            col = 0
            worksheet.col(col).width = int(25 * 260)
            worksheet.write(row, col, "Refund")
            worksheet.write(row, col + 1, grand_journal_dic.get('Refund', 0.0))
        filename = 'POS Payment Report.xls'
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
            attachment.sudo().write(attachment_vals)
        else:
            attachment = ir_attachment.create(attachment_vals)

        url = "/web/content/" + \
            str(attachment.id) + "?download=true"
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }

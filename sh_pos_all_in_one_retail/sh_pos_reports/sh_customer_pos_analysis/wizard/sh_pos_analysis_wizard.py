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


class POSAnalysisWizard(models.TransientModel):
    _name = 'sh.pos.analysis.wizard'
    _description = 'POS Analysis Wizard'

    sh_start_date = fields.Datetime(
        'Start Date', required=True, default=fields.Datetime.now)
    sh_end_date = fields.Datetime(
        'End Date', required=True, default=fields.Datetime.now)
    sh_partner_ids = fields.Many2many(
        'res.partner', string='Customers', required=True)
    sh_status = fields.Selection([('all', 'All'), ('draft', 'Draft'), ('paid', 'Paid'), (
        'done', 'Posted'), ('invoiced', 'Invoiced')], string="Status", default='all')
    report_by = fields.Selection(
        [('order', 'POS Order'), ('product', 'Products')], string='Report Print By', default='order')
    sh_product_ids = fields.Many2many('product.product', string='Products')
    sh_session_id = fields.Many2one('pos.session', 'Session')
    company_ids = fields.Many2many(
        'res.company', default=lambda self: self.env.companies, string="Companies")

    @api.constrains('sh_start_date', 'sh_end_date')
    def _check_dates(self):
        if self.filtered(lambda c: c.sh_end_date and c.sh_start_date > c.sh_end_date):
            raise ValidationError(_('start date must be less than end date.'))

    def print_report(self):
        datas = self.read()[0]
        return self.env.ref('sh_pos_all_in_one_retail.sh_cus_pos_analysis_action').report_action([], data=datas)

    def display_report(self):
        datas = self.read()[0]
        report = self.env['report.sh_pos_all_in_one_retail.sh_cus_pos_analysis_doc']
        data_values = report._get_report_values(
            docids=None, data=datas).get('order_dic_by_orders')
        data_values_by_products = report._get_report_values(
            docids=None, data=datas).get('order_dic_by_products')

        # Order
        if self.report_by == "order":
            self.env['sh.customer.pos.analysis.order'].search([]).unlink()
            if data_values:
                for customer in data_values:
                    for order in data_values[customer]:
                        self.env['sh.customer.pos.analysis.order'].create({
                            'sh_partner_id': order['partner_id'],
                            'name': order['order_number'],
                            'order_date': order['order_date'],
                            'user_id': order['salesperson_id'],
                            'sales_amount': order['sale_amount'],
                            'amount_paid': order['paid_amount'],
                            'balance': order['balance_amount']
                        })
            return {
                'type': 'ir.actions.act_window',
                'name': 'Customer Sales Analysis',
                'view_mode': 'tree',
                'res_model': 'sh.customer.pos.analysis.order',
                'context': "{'create': False,'search_default_group_customer': 1}"
            }

        # Product
        if self.report_by == "product":
            self.env['sh.customer.pos.analysis.product'].search([]).unlink()
            if data_values_by_products:
                for product in data_values_by_products:
                    for order in data_values_by_products[product]:
                        self.env['sh.customer.pos.analysis.product'].create({
                            'sh_partner_id': order['partner_id'],
                            'name': order['order_number'],
                            'date': order['order_date'],
                            'sh_product_id': order['product_id'],
                            'price': order['price'],
                            'quantity': order['qty'],
                            'discount': order['discount'],
                            'tax': order['tax'],
                            'subtotal': order['subtotal']
                        })
            return {
                'type': 'ir.actions.act_window',
                'name': 'Customer Sales Analysis',
                'view_mode': 'tree',
                'res_model': 'sh.customer.pos.analysis.product',
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
            'Customer Point Of Sale Analysis', bold_center)
        left = easyxf('align: horiz center;font:bold True')
        center = easyxf('align: horiz center;')
        bold_center_total = easyxf('align: horiz center;font:bold True')
        user_tz = self.env.user.tz or utc
        local = timezone(user_tz)
        start_date = datetime.strftime(utc.localize(datetime.strptime(str(
            self.sh_start_date), DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local), DEFAULT_SERVER_DATETIME_FORMAT)
        end_date = datetime.strftime(utc.localize(datetime.strptime(str(
            self.sh_end_date), DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local), DEFAULT_SERVER_DATETIME_FORMAT)
        if self.report_by == 'order':
            worksheet.write_merge(
                0, 1, 0, 5, 'Customer Point Of Sale Analysis', heading_format)
            worksheet.write_merge(
                2, 2, 0, 5, start_date + " to " + end_date, bold)
        elif self.report_by == 'product':
            worksheet.write_merge(
                0, 1, 0, 7, 'Customer Point Of Sale Analysis', heading_format)
            worksheet.write_merge(
                2, 2, 0, 7, start_date + " to " + end_date, bold)
        worksheet.col(0).width = int(25 * 260)
        worksheet.col(1).width = int(25 * 260)
        worksheet.col(2).width = int(
            25 * 260) if self.report_by == 'order' else int(33 * 260)
        worksheet.col(3).width = int(25 * 260)
        worksheet.col(4).width = int(25 * 260)
        worksheet.col(5).width = int(25 * 260)
        worksheet.col(6).width = int(25 * 260)
        worksheet.col(7).width = int(25 * 260)

        datas = self.read()[0]
        report = self.env['report.sh_pos_all_in_one_retail.sh_cus_pos_analysis_doc']
        order_dic_by_orders = report._get_report_values(
            docids=None, data=datas).get('order_dic_by_orders')
        order_dic_by_products = report._get_report_values(
            docids=None, data=datas).get('order_dic_by_products')

        row = 4
        if self.report_by == 'order':
            if order_dic_by_orders:
                for key in order_dic_by_orders.keys():
                    worksheet.write_merge(
                        row, row, 0, 5, key, bold_center)
                    row = row + 2
                    total_sale_amount = 0.0
                    total_amount_paid = 0.0
                    total_balance = 0.0
                    worksheet.write(row, 0, "Order Number", bold)
                    worksheet.write(row, 1, "Order Date", bold)
                    worksheet.write(row, 2, "Salesperson", bold)
                    worksheet.write(row, 3, "Sales Amount", bold)
                    worksheet.write(row, 4, "Amount Paid", bold)
                    worksheet.write(row, 5, "Balance", bold)
                    row = row + 1
                    for rec in order_dic_by_orders[key]:
                        worksheet.write(row, 0, rec.get(
                            'order_number'), center)
                        worksheet.write(row, 1, str(
                            rec.get('order_date')), center)
                        worksheet.write(row, 2, rec.get('salesperson'), center)
                        worksheet.write(row, 3, str(
                            rec.get('sale_currency_symbol'))+str("{:.2f}".format(rec.get('sale_amount'))), center)
                        worksheet.write(row, 4, str(
                            rec.get('sale_currency_symbol')) + str("{:.2f}".format(rec.get('paid_amount'))), center)
                        worksheet.write(row, 5, str(
                            rec.get('sale_currency_symbol')) + str("{:.2f}".format(rec.get('balance_amount'))), center)
                        total_sale_amount = total_sale_amount + \
                            rec.get('sale_amount')
                        total_amount_paid = total_amount_paid + \
                            rec.get('paid_amount')
                        total_balance = total_balance + \
                            rec.get('balance_amount')
                        row = row + 1
                    worksheet.write(row, 2, "Total", left)
                    worksheet.write(row, 3, "{:.2f}".format(total_sale_amount),
                                    bold_center_total)
                    worksheet.write(row, 4, "{:.2f}".format(total_amount_paid),
                                    bold_center_total)
                    worksheet.write(row, 5, "{:.2f}".format(
                        total_balance), bold_center_total)
                    row = row + 2
        elif self.report_by == 'product':
            if order_dic_by_products:
                for key in order_dic_by_products.keys():
                    worksheet.write_merge(
                        row, row, 0, 7, key, bold_center)
                    row = row + 2
                    total_tax = 0.0
                    total_subtotal = 0.0
                    total_balance = 0.0
                    worksheet.write(row, 0, "Number", bold)
                    worksheet.write(row, 1, "Date", bold)
                    worksheet.write(row, 2, "Product", bold)
                    worksheet.write(row, 3, "Price", bold)
                    worksheet.write(row, 4, "Quantity", bold)
                    worksheet.write(row, 5, "Disc.(%)", bold)
                    worksheet.write(row, 6, "Tax", bold)
                    worksheet.write(row, 7, "Subtotal", bold)
                    row = row + 1
                    for rec in order_dic_by_products[key]:
                        worksheet.write(row, 0, rec.get(
                            'order_number'), center)
                        worksheet.write(row, 1, str(
                            rec.get('order_date')), center)
                        worksheet.write(row, 2, rec.get(
                            'product_name'), center)
                        worksheet.write(row, 3, str(
                            rec.get('sale_currency_symbol'))+str("{:.2f}".format(rec.get('price'))), center)
                        worksheet.write(row, 4, rec.get('qty'), center)
                        worksheet.write(row, 5, rec.get('discount'), center)
                        worksheet.write(row, 6, str(
                            rec.get('sale_currency_symbol'))+str("{:.2f}".format(rec.get('tax'))), center)
                        worksheet.write(row, 7, str(
                            rec.get('sale_currency_symbol'))+str("{:.2f}".format(rec.get('subtotal'))), center)
                        total_tax = total_tax + rec.get('tax')
                        total_subtotal = total_subtotal + rec.get('subtotal')
                        row = row + 1
                    worksheet.write(row, 5, "Total", left)
                    worksheet.write(row, 6, "{:.2f}".format(
                        total_tax), bold_center_total)
                    worksheet.write(row, 7, "{:.2f}".format(
                        total_subtotal), bold_center_total)
                    row = row + 2

        filename = 'Customer Point of Sale Analysis.xls'
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

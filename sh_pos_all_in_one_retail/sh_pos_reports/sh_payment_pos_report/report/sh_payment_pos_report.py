# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from datetime import timedelta
from pytz import timezone
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PaymentReport(models.AbstractModel):
    _name = 'report.sh_pos_all_in_one_retail.sh_payment_pos_report_doc'
    _description = 'POS payment report abstract model'

    @api.model
    def _get_report_values(self, docids, data=None):
        data = dict(data or {})
        if data['date_start']:
            date_start = fields.Datetime.from_string(data['date_start'])
        else:
            # start by default today 00:00:00
            user_tz = timezone(self.env.context.get(
                'tz') or self.env.user.tz or 'UTC')
            today = user_tz.localize(fields.Datetime.from_string(
                fields.Date.context_today(self)))
            date_start = today.astimezone(timezone('UTC'))

        if data['date_end']:
            date_stop = fields.Datetime.from_string(data['date_end'])
            # avoid a date_stop smaller than date_start
            if date_stop < date_start:
                date_stop = date_start + timedelta(days=1, seconds=-1)
        else:
            # stop by default today 23:59:59
            date_stop = date_start + timedelta(days=1, seconds=-1)
        account_payment_obj = self.env["pos.payment"]
        account_journal_obj = self.env["pos.payment.method"]

        journal_domain = []
        if data.get('company_ids', False):
            journal_domain.append(
                ('company_id', 'in', data.get('company_ids', False)))
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

        currency = False
        grand_journal_dic = {}
        j_refund = 0.0

        user_data_dic = {}
        if data.get("user_ids", False):
            for user_id in data.get("user_ids"):
                domain = [
                    ("payment_date", ">=", fields.Datetime.to_string(date_start)),
                    ("payment_date", "<=", fields.Datetime.to_string(date_stop)),
                ]
                if data.get("state", False):
                    state = data.get("state")
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
                    ("pos_order_id.user_id", "=", user_id))
                if data.get('company_ids', False):
                    domain.append(
                        ("company_id", "in", data.get('company_ids', False)))
                if data.get('config_ids', False):
                    session_ids = self.env['pos.session'].sudo().search(
                        [('config_id', 'in', data.get('config_ids', False))])
                    domain.append(
                        ("pos_order_id.session_id", "in", session_ids.ids))
                payments = account_payment_obj.sudo().search(domain)
                invoice_pay_dic = {}
                if payments and search_journals:
                    for journal in search_journals:
                        # journal wise payment first we total all bank, cash etc etc.
                        for journal_wise_payment in payments.filtered(lambda x: x.payment_method_id.id == journal.id):
                            if data.get('filter_invoice_data') and data.get('filter_invoice_data') == 'all':
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
                                                                                       "Customer": invoice.partner_id.name if invoice.partner_id else 'Walking Customer',
                                                                                       "Customer_id": invoice.partner_id.id, "Invoice Date": invoice.invoice_date, "User": invoice.user_id.name if invoice.user_id else "", "User_id": invoice.user_id.id if invoice.user_id else "", "style": 'border: 1px solid black;'}})
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
                                                                                       "Customer": invoice.partner_id.name if invoice.partner_id else 'Walking Customer', "Customer_id": invoice.partner_id.id, "Invoice Date": invoice.invoice_date, "User": invoice.user_id.name if invoice.user_id else "", "User_id": invoice.user_id.id if invoice.user_id else "",  "style": 'border: 1px solid black;color:red'}})
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
                                                                                                         "Customer": journal_wise_payment.pos_order_id.partner_id.name if journal_wise_payment.pos_order_id.partner_id else 'Walking Customer', "Customer_id": journal_wise_payment.pos_order_id.partner_id.id,  "Invoice Date": journal_wise_payment.payment_date.date(), "User": journal_wise_payment.pos_order_id.user_id.name if journal_wise_payment.pos_order_id.user_id else "", "User_id": journal_wise_payment.pos_order_id.user_id.id if journal_wise_payment.pos_order_id.user_id else "",  "style": 'border: 1px solid black;'}})
                            elif data.get('filter_invoice_data') and data.get('filter_invoice_data') == 'with_invoice':
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
                                                                                       "Customer": invoice.partner_id.name if invoice.partner_id else 'Walking Customer', "Customer_id": invoice.partner_id.id, "Invoice Date": invoice.invoice_date, "User": invoice.user_id.name if invoice.user_id else "", "User_id": invoice.user_id.id if invoice.user_id else "", "style": 'border: 1px solid black;'}})
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
                                                                                       "Customer": invoice.partner_id.name if invoice.partner_id else 'Walking Customer', "Customer_id": invoice.partner_id.id, "Invoice Date": invoice.invoice_date, "User": invoice.user_id.name if invoice.user_id else "", "User_id": invoice.user_id.id if invoice.user_id else "", "style": 'border: 1px solid black;color:red'}})
                            elif data.get('filter_invoice_data') and data.get('filter_invoice_data') == 'wo_invoice':
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
                                                                                                         "Customer": journal_wise_payment.pos_order_id.partner_id.name if journal_wise_payment.pos_order_id.partner_id else 'Walking Customer', "Customer_id": journal_wise_payment.pos_order_id.partner_id.id, "Invoice Date": journal_wise_payment.payment_date.date(), "User": journal_wise_payment.pos_order_id.user_id.name if journal_wise_payment.pos_order_id.user_id else "", "User_id": journal_wise_payment.pos_order_id.user_id.id if journal_wise_payment.pos_order_id.user_id else "", "style": 'border: 1px solid black;'}})
                # all final list and [{},{},{}] format
                # here we get the below total.
                # total journal amount is a grand total and format is : {} just a dictionary
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

                # finally make user wise dic here.
                search_user = self.env['res.users'].sudo().search([
                    ('id', '=', user_id)
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
        if not user_data_dic:
            raise UserError(_(
                'There is no Data Found between these dates...'))
        data.update({
            'date_start': data['date_start'],
            'date_end': data['date_end'],
            'columns': final_col_list,
            'user_data_dic': user_data_dic,
            'currency': currency,
            'grand_journal_dic': grand_journal_dic,
        })
        return data

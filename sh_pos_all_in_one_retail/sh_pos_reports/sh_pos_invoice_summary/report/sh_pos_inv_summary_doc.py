# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from datetime import timedelta
from pytz import timezone
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class POSINVSummary(models.AbstractModel):
    _name = 'report.sh_pos_all_in_one_retail.sh_pos_inv_summary_doc'
    _description = 'POS Invoice Summary report abstract model'

    @api.model
    def _get_report_values(self, docids, data=None):
        data = dict(data or {})
        pos_order_obj = self.env["pos.order"]
        customer_order_dic = {}
        if data['sh_start_date']:
            date_start = fields.Datetime.from_string(data['sh_start_date'])
        else:
            # start by default today 00:00:00
            user_tz = timezone(self.env.context.get(
                'tz') or self.env.user.tz or 'UTC')
            today = user_tz.localize(fields.Datetime.from_string(
                fields.Date.context_today(self)))
            date_start = today.astimezone(timezone('UTC'))

        if data['sh_end_date']:
            date_stop = fields.Datetime.from_string(data['sh_end_date'])
            # avoid a date_stop smaller than date_start
            if date_stop < date_start:
                date_stop = date_start + timedelta(days=1, seconds=-1)
        else:
            # stop by default today 23:59:59
            date_stop = date_start + timedelta(days=1, seconds=-1)
        if data.get('sh_partner_ids', False):
            for partner_id in data.get('sh_partner_ids'):
                order_list = []
                domain = [
                    ("date_order", ">=", fields.Datetime.to_string(date_start)),
                    ("date_order", "<=", fields.Datetime.to_string(date_stop)),
                    ('state', 'not in', ['draft', 'cancel']),
                    ('partner_id', '=', partner_id)
                ]
                if data.get('sh_status') == 'both':
                    domain.append(('account_move.state', 'in', ['posted']))
                elif data.get('sh_status') == 'open':
                    domain.append(('account_move.state', 'in', ['posted']))
                    domain.append(('account_move.amount_residual', '!=', 0.0))
                elif data.get('sh_status') == 'paid':
                    domain.append(('account_move.state', 'in', ['posted']))
                    domain.append(('account_move.amount_residual', '=', 0.0))
                if data.get('company_ids', False):
                    domain.append(
                        ('company_id', 'in', data.get('company_ids', False)))
                if data.get('sh_session_id', False):
                    domain.append(
                        ('session_id', '=', data.get('sh_session_id', False)[0]))
                search_orders = pos_order_obj.sudo().search(domain)
                invoice_ids = []
                if search_orders:
                    for order in search_orders:
                        if order.payment_ids:
                            for invoice in order.account_move:
                                if invoice.id not in invoice_ids:
                                    invoice_ids.append(invoice.id)
                                order_dic = {
                                    'order_number': order.name,
                                    'order_date': order.date_order,
                                    'partner_id': order.partner_id.id if order.partner_id else False,
                                    'invoice_number': invoice.name,
                                    'invoice_date': invoice.invoice_date,
                                    'invoice_currency_id': invoice.currency_id.id,
                                    'invoice_currency_symbol': invoice.currency_id.symbol,  # For Excel Report
                                }
                                invoice_amount = 0.0
                                if order.payment_ids:
                                    for invoice in order.payment_ids:
                                        invoice_amount = invoice_amount+invoice.amount
                                        invoice_paid_amount = invoice.amount
                                        due_amount = order.amount_total-invoice.amount
                                order_dic.update({
                                    'invoice_amount': float("{:.2f}".format(invoice_amount)),
                                    'invoice_paid_amount': float("{:.2f}".format(invoice_paid_amount)),
                                    'due_amount': float("{:.2f}".format(due_amount)),
                                })
                                order_list.append(order_dic)
                search_partner = self.env['res.partner'].sudo().search([
                    ('id', '=', partner_id)
                ], limit=1)
                if search_partner and order_list:
                    customer_order_dic.update(
                        {search_partner.display_name: order_list})
        if not customer_order_dic:
            raise UserError(_(
                'There is no Data Found between these dates...'))
        data.update({
            'date_start': data['sh_start_date'],
            'date_end': data['sh_end_date'],
            'customer_order_dic': customer_order_dic,
        })
        return data

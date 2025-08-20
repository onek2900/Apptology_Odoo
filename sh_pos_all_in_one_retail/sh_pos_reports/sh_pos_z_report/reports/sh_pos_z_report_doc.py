# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from odoo import api, models, fields
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT


class UserReport(models.AbstractModel):
    _name = 'report.sh_pos_all_in_one_retail.sh_pos_z_report_doc'
    _description = "pos person report abstract model"

    def get_product_name(self, product_id):
        if product_id:
            product = self.env['product.product'].search(
                [('id', '=', product_id)])
            if product:
                return product.display_name
        return False

    def get_current_datetime(self):
        current = fields.datetime.now()
        return current.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

    @api.model
    def _get_report_values(self, docids, data=None):

        session_id = 0

        final_session_data = []

        if data and data.get('pos_session_id'):
            session_id = self.env['pos.session'].browse(
                data.get('pos_session_id'))

        if session_id:
            for session_id in session_id:
                total_cash_in = 0
                total_cash_out = 0
                order_ids = []
                partner_ids = []
                total_partner = 0
                sold_product = {}
                total_discount = 0
                total_tax = 0
                total_return_amount = 0
                session_data = {}
                statement_line = self.env['account.bank.statement.line'].search(
                    [('pos_session_id', '=', session_id.id)])

                if statement_line:
                    for each_statement in statement_line:
                        if each_statement.payment_ref:
                            splited_payment_ref = each_statement.payment_ref.split(
                                '-')
                            if splited_payment_ref and len(splited_payment_ref) > 1:
                                if splited_payment_ref[1]:
                                    if splited_payment_ref[1] == 'in':
                                        total_cash_in = total_cash_in + each_statement.amount
                                    if splited_payment_ref[1] == 'out':
                                        total_cash_out = total_cash_out - each_statement.amount
                if session_id.order_ids:
                    for each_order in session_id.order_ids:
                        order_ids.append(each_order.id)
                        if each_order.partner_id:
                            if each_order.partner_id.id not in partner_ids:
                                partner_ids.append(each_order.partner_id.id)
                                total_partner = total_partner + 1
                        if each_order and each_order.amount_tax:
                            total_tax = total_tax + each_order.amount_tax
                        if each_order and each_order.lines:
                            for each_order_line in each_order.lines:
                                if each_order_line:
                                    if data and data.get('category_wise'):
                                        if each_order_line.product_id.pos_categ_ids:
                                            for each_categ in each_order_line.product_id.pos_categ_ids:
                                                if each_categ.name:
                                                    if each_categ.name in sold_product:
                                                        sold_product[each_categ.name]['qty'] += each_order_line.qty
                                                        sold_product[each_categ.name]['price'] += each_order_line.price_subtotal_incl
                                                    else:
                                                        sold_product.update({each_categ.name: {
                                                                            'qty': each_order_line.qty, 'price': each_order_line.price_subtotal_incl}})
                                        else:
                                            if 'No Category' in sold_product:
                                                sold_product['No Category']['qty'] += each_order_line.qty
                                                sold_product['No Category']['price'] += each_order_line.price_subtotal_incl
                                            else:
                                                sold_product.update({'No Category': {
                                                                    'qty': each_order_line.qty, 'price': each_order_line.price_subtotal_incl}})
                                    if each_order_line.price_subtotal_incl and each_order_line.price_subtotal_incl < 0:
                                        total_return_amount = total_return_amount - \
                                            (each_order_line.price_subtotal_incl)
                                    if each_order_line.discount:
                                        total_discount = total_discount + \
                                            ((each_order_line.price_unit * each_order_line.qty) -
                                             each_order_line.price_subtotal_incl)
                if data and data.get('payment_wise'):
                    payments = 0
                    if order_ids:
                        payment_ids = self.env["pos.payment"].search(
                            [('pos_order_id', 'in', order_ids)]).ids
                        if payment_ids:
                            self.env.cr.execute("""
                                SELECT COALESCE(method.name->>%s, method.name->>'en_US') as name, sum(amount) total
                                FROM pos_payment AS payment,
                                    pos_payment_method AS method
                                WHERE payment.payment_method_id = method.id
                                    AND payment.id IN %s
                                GROUP BY method.name
                            """, (self.env.lang, tuple(payment_ids),))
                            payments = self.env.cr.dictfetchall()
                        else:
                            payments = []
                    session_data['payment_detail'] = payments
                if data and data.get('customer_wise'):
                    customer_orders = 0
                    if session_id.order_ids:
                        if order_ids:
                            self.env.cr.execute("""
                                SELECT partner.name as name, sum(amount_total) total
                                FROM pos_order AS payment,
                                    res_partner AS partner
                                WHERE payment.partner_id = partner.id
                                    AND payment.id IN %s
                                GROUP BY partner.name
                            """, (tuple(order_ids),))
                            customer_orders = self.env.cr.dictfetchall()
                        else:
                            customer_orders = []
                    session_data['customer_detail'] = customer_orders

                if data and data.get('product_wise'):
                    products_detail = 0
                    if session_id.order_ids:
                        if order_ids:
                            self.env.cr.execute("""select line.product_id as product_id, sum(price_subtotal_incl) as total, sum(qty) as quantity from pos_order_line AS line where order_id in %s GROUP BY line.product_id
                                """, (tuple(order_ids),))
                            products_detail = self.env.cr.dictfetchall()
                        else:
                            products_detail = []
                    session_data['products_detail'] = products_detail
                session_data['total_no_order'] = len(order_ids)
                session_data['total_partner'] = total_partner
                session_data['sold_product'] = sold_product
                session_data['current_date_time'] = self.get_current_datetime()
                session_data['total_discount'] = total_discount
                session_data['total_tax'] = total_tax
                session_data['total_return_amount'] = total_return_amount
                session_data['name'] = session_id.name
                session_data['config_id'] = session_id.config_id.name
                session_data['state'] = session_id.state
                session_data['start_at'] = session_id.start_at
                session_data['cash_register_balance_start'] = session_id.cash_register_balance_start
                session_data['total_payments_amount'] = session_id.total_payments_amount
                session_data['cash_register_balance_end'] = session_id.cash_register_balance_end
                session_data['cash_register_difference'] = session_id.cash_register_difference
                session_data['stop_at'] = session_id.stop_at
                session_data['saleperson'] = session_id.user_id.name
                session_data['session_name'] = session_id.name
                session_data['currency'] = self.env.company.sudo().currency_id
                session_data['is_display_category_wise'] = data.get(
                    'category_wise')
                session_data['is_display_product_wise'] = data.get(
                    'product_wise')
                session_data['is_display_customer_wise'] = data.get(
                    'customer_wise')
                session_data['is_display_payment_wise'] = data.get(
                    'payment_wise')
                session_data['total_cash_in'] = total_cash_in
                session_data['total_cash_out'] = total_cash_out
                final_session_data.append(session_data)
        data = {'session_detail': final_session_data}
        return data

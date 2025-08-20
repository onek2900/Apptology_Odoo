# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from odoo import models, fields, api
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT


class PosSession(models.Model):
    _inherit = 'pos.session'

    def load_pos_data(self):
        pos_data = super(PosSession, self).load_pos_data()
        posted_session = self.search_read(
            [('state', '=', 'closed'), ('user_id', '=', self.env.user.id)], ['id', 'name'])
        if posted_session:
            pos_data['posted_session'] = posted_session
        return pos_data

    def _loader_params_hr_employee(self):
        result = super()._loader_params_hr_employee()
        if result:
            if result.get('search_params') and result.get('search_params').get('fields'):
                result.get('search_params').get(
                    'fields').append('sh_is_allow_z_report')
        return result

    def _loader_params_res_users(self):
        result = super()._loader_params_res_users()
        if result:
            if result.get('search_params') and result.get('search_params').get('fields'):
                result.get('search_params').get(
                    'fields').append('sh_is_allow_z_report')
        return result

    def _loader_params_pos_session(self):
        result = super()._loader_params_pos_session()
        if result:
            if result.get('search_params') and result.get('search_params').get('fields'):
                result.get('search_params').get(
                    'fields').append('total_payments_amount')
                result.get('search_params').get(
                    'fields').append('cash_register_balance_end')
                result.get('search_params').get(
                    'fields').append('cash_register_difference')
        return result

    def get_current_datetime(self):
        current = fields.datetime.now()
        return current.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

    def get_product_name(self, product_id):
        if product_id:
            product = self.env['product.product'].search(
                [('id', '=', product_id)])
            if product:
                return product.display_name
        return False

    @api.model
    def get_session_detail(self, session_id):
        data = {}
        order_ids = []
        partner_ids = []
        total_partner = 0
        sold_product = {}
        total_discount = 0
        total_tax = 0
        total_return_amount = 0
        total_cash_in = 0
        total_cash_out = 0

        if isinstance(session_id, int):
            session_id = self.browse(session_id)
        if session_id:
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
                                if session_id.config_id.sh_display_category_wise_detail:
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
            if session_id.config_id and session_id.config_id.sh_display_payment_detail:
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
                        # data['payment_detail'] = payments
                    else:
                        payments = []
                data['payment_detail'] = payments
            if session_id.config_id and session_id.config_id.sh_display_customer_wise_detail:
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
                data['customer_detail'] = customer_orders

            if session_id.config_id and session_id.config_id.sh_display_product_wise_detail:
                products_detail = 0
                if session_id.order_ids:
                    if order_ids:
                        self.env.cr.execute("""select line.product_id as product_id, sum(price_subtotal_incl) as total, sum(qty) as quantity from pos_order_line AS line where order_id in %s GROUP BY line.product_id
                            """, (tuple(order_ids),))
                        products_detail = self.env.cr.dictfetchall()
                    else:
                        products_detail = []
                data['products_detail'] = products_detail
        data['total_no_order'] = len(order_ids)
        data['total_partner'] = total_partner
        data['sold_product'] = sold_product
        data['current_date_time'] = self.get_current_datetime()
        data['total_discount'] = total_discount
        data['total_tax'] = total_tax
        data['total_return_amount'] = total_return_amount
        data['name'] = session_id.name
        data['config_id'] = session_id.config_id.name
        data['state'] = session_id.state
        data['start_at'] = session_id.start_at
        data['cash_register_balance_start'] = session_id.cash_register_balance_start
        data['total_payments_amount'] = session_id.total_payments_amount
        data['cash_register_balance_end'] = session_id.cash_register_balance_end
        data['cash_register_difference'] = session_id.cash_register_difference
        data['stop_at'] = session_id.stop_at
        data['total_cash_in'] = total_cash_in
        data['total_cash_out'] = total_cash_out
        return data

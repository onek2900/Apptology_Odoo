# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from datetime import timedelta
from pytz import timezone
from odoo import api, models, fields
from odoo.exceptions import UserError


class POSProductProfitAnalysis(models.AbstractModel):
    _name = 'report.sh_pos_all_in_one_retail.sh_pos_product_profit_doc'
    _description = 'Point of Sale Product Profit report abstract model'

    @api.model
    def _get_report_values(self, docids, data=None):
        data = dict(data or {})
        order_dic_by_customers = {}
        order_dic_by_products = {}
        both_order_list = []
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
        if data.get('report_by') == 'customer':
            if data.get('sh_partner_ids', False):
                partners = self.env['res.partner'].sudo().browse(
                    data.get('sh_partner_ids', False))
            else:
                partners = self.env['res.partner'].sudo().search([])
            if partners:
                for partner_id in partners:
                    order_list = []
                    domain = [
                        ("date_order", ">=", fields.Datetime.to_string(date_start)),
                        ("date_order", "<=", fields.Datetime.to_string(date_stop)),
                        ("partner_id", "=", partner_id.id),
                        ('state', 'not in', ['draft', 'cancel'])
                    ]
                    if data.get('company_ids', False):
                        domain.append(
                            ('company_id', 'in', data.get('company_ids', False)))
                    if data.get('sh_session_id', False):
                        domain.append(
                            ('session_id', '=', data.get('sh_session_id', False)[0]))
                    search_orders = self.env['pos.order'].sudo().search(domain)
                    if search_orders:
                        for order in search_orders:
                            if order.lines:
                                order_dic = {}
                                for line in order.lines:
                                    line_dic = {
                                        'order_number': order.name,
                                        'order_date': order.date_order,
                                        'partner_id': order.partner_id.id,
                                        'product': line.product_id.display_name,
                                        'product_id': line.product_id.id,
                                        'qty': float("{:.2f}".format(line.qty)),
                                        'cost': float("{:.2f}".format(line.product_id.standard_price)),
                                        'sale_price': float("{:.2f}".format(line.price_unit)),
                                    }
                                    if order_dic.get(line.product_id.id, False):
                                        qty = order_dic.get(
                                            line.product_id.id)['qty']
                                        qty = qty + line.qty
                                        line_dic.update({
                                            'qty': float("{:.2f}".format(qty)),
                                        })
                                    order_dic.update(
                                        {line.product_id.id: line_dic})
                                for value in order_dic.values():
                                    order_list.append(value)
                    if partner_id and order_list:
                        order_dic_by_customers.update(
                            {partner_id.display_name: order_list})
            if order_dic_by_customers:
                data.update({
                    'date_start': data['sh_start_date'],
                    'date_end': data['sh_end_date'],
                    'order_dic_by_customers': order_dic_by_customers,
                })
                return data
            else:
                raise UserError(
                    'There is no Data Found between these dates...')

        elif data.get('report_by') == 'product':
            if data.get('sh_product_ids', False):
                products = self.env['product.product'].sudo().browse(
                    data.get('sh_product_ids', False))
            else:
                products = self.env['product.product'].sudo().search([])
            if products:
                for product_id in products:
                    order_list = []
                    domain = [
                        ("date_order", ">=", fields.Datetime.to_string(date_start)),
                        ("date_order", "<=", fields.Datetime.to_string(date_stop)),
                        ('state', 'not in', ['draft', 'cancel'])
                    ]
                    if data.get('company_ids', False):
                        domain.append(
                            ('company_id', 'in', data.get('company_ids', False)))
                    if data.get('sh_session_id', False):
                        domain.append(
                            ('session_id', '=', data.get('sh_session_id', False)[0]))
                    search_orders = self.env['pos.order'].sudo().search(domain)
                    if search_orders:
                        for order in search_orders:
                            if order.lines:
                                order_dic = {}
                                for line in order.lines.sudo().filtered(lambda x: x.product_id.id == product_id.id):
                                    line_dic = {
                                        'order_number': order.name,
                                        'order_date': order.date_order,
                                        'customer': order.partner_id.display_name if order.partner_id else "",
                                        'partner_id': order.partner_id.id if order.partner_id else False,
                                        'product_id': line.product_id.id,
                                        'qty': float("{:.2f}".format(line.qty)),
                                        'cost': float("{:.2f}".format(line.product_id.standard_price)),
                                        'sale_price': float("{:.2f}".format(line.price_unit)),
                                    }
                                    if order_dic.get(line.product_id.id, False):
                                        qty = order_dic.get(
                                            line.product_id.id)['qty']
                                        qty = qty + line.qty
                                        line_dic.update({
                                            'qty': float("{:.2f}".format(qty)),
                                        })
                                    order_dic.update(
                                        {line.product_id.id: line_dic})
                                for value in order_dic.values():
                                    order_list.append(value)
                    if product_id and order_list:
                        order_dic_by_products.update(
                            {product_id.display_name: order_list})
            if order_dic_by_products:
                data.update({
                    'date_start': data['sh_start_date'],
                    'date_end': data['sh_end_date'],
                    'order_dic_by_products': order_dic_by_products,
                })
                return data
            else:
                raise UserError(
                    'There is no Data Found between these dates...')

        elif data.get('report_by') == 'both':
            if data.get('sh_product_ids', False):
                products = self.env['product.product'].sudo().browse(
                    data.get('sh_product_ids', False))
            else:
                products = self.env['product.product'].sudo().search([])
            if data.get('sh_partner_ids', False):
                partners = self.env['res.partner'].sudo().browse(
                    data.get('sh_partner_ids', False))
            else:
                partners = self.env['res.partner'].sudo().search([])
            domain = [
                ("date_order", ">=", fields.Datetime.to_string(date_start)),
                ("date_order", "<=", fields.Datetime.to_string(date_stop)),
                ('state', 'not in', ['draft', 'cancel'])
            ]
            if data.get('company_ids', False):
                domain.append(
                    ('company_id', 'in', data.get('company_ids', False)))
            if data.get('sh_session_id', False):
                domain.append(
                    ('session_id', '=', data.get('sh_session_id', False)[0]))
            search_orders = self.env['pos.order'].sudo().search(domain)
            if search_orders:
                for order in search_orders.sudo().filtered(lambda x: x.partner_id.id in partners.ids):
                    if order.lines:
                        order_dic = {}
                        for line in order.lines.sudo().filtered(lambda x: x.product_id.id in products.ids):
                            line_dic = {
                                'order_number': order.name,
                                'order_date': order.date_order,
                                'customer': order.partner_id.display_name,
                                'partner_id': order.partner_id.id,
                                'product': line.product_id.display_name,
                                'product_id': line.product_id.id,
                                'qty': float("{:.2f}".format(line.qty)),
                                'cost': float("{:.2f}".format(line.product_id.standard_price)),
                                'sale_price': float("{:.2f}".format(line.price_unit)),
                            }
                            if order_dic.get(line.product_id.id, False):
                                qty = order_dic.get(line.product_id.id)['qty']
                                qty = qty + line.qty
                                line_dic.update({
                                    'qty': float("{:.2f}".format(qty)),
                                })
                            order_dic.update({line.product_id.id: line_dic})
                        if order_dic:
                            for value in order_dic.values():
                                both_order_list.append(value)
            if both_order_list:
                data.update({
                    'date_start': data['sh_start_date'],
                    'date_end': data['sh_end_date'],
                    'both_order_list': both_order_list,
                })
                return data
            else:
                raise UserError(
                    'There is no Data Found between these dates...')

        data.update({
            'report_by': data.get('report_by'),
        })
        return data

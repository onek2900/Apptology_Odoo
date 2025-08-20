# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from datetime import timedelta
from pytz import timezone
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class POSByCategory(models.AbstractModel):
    _name = 'report.sh_pos_all_in_one_retail.sh_pos_by_category_doc'
    _description = 'Point of Sale by category report abstract model'

    @api.model
    def _get_report_values(self, docids, data=None):
        data = dict(data or {})
        pos_order_obj = self.env["pos.order"]
        category_order_dic = {}
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
        if data.get('sh_category_ids', False):
            categories = self.env['pos.category'].sudo().browse(
                data.get('sh_category_ids', False))
        else:
            categories = self.env['pos.category'].sudo().search([])
        if categories:
            for category in categories:
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
                search_orders = pos_order_obj.sudo().search(domain)
                if search_orders:
                    for order in search_orders:
                        if order.lines:
                            order_dic = {}
                            for line in order.lines.sudo().filtered(lambda x: x.product_id.pos_categ_ids.id == category.id):
                                line_dic = {
                                    'order_number': order.name,
                                    'order_date': order.date_order,
                                    'product': line.product_id.display_name, 'product_id': line.product_id.id,
                                    'category_id': line.product_id.pos_categ_ids.id if line.product_id.pos_categ_ids else False,
                                    'qty': float("{:.2f}".format(line.qty)),
                                    'discount': float("{:.2f}".format(line.discount)),
                                    'uom': line.product_uom_id.name,
                                    'uom_id': line.product_uom_id.id,
                                    'sale_price': float("{:.2f}".format(line.price_unit)),
                                    'sale_price_subtotal': float("{:.2f}".format(line.price_subtotal)),
                                    'sale_price_total': float("{:.2f}".format(line.price_subtotal_incl)),
                                    'tax': float("{:.2f}".format(line.price_subtotal_incl - line.price_subtotal)),
                                    'sale_currency_id': line.currency_id.id,
                                    'sale_currency_symbol': line.currency_id.symbol,  # For Excel Report
                                }
                                if order_dic.get(line.product_id.id, False):
                                    qty = order_dic.get(
                                        line.product_id.id)['qty']
                                    qty = qty + line.qty
                                    tax = order_dic.get(
                                        line.product_id.id)['tax']
                                    tax = tax + line.price_subtotal_incl - line.price_subtotal
                                    line_dic.update({
                                        'qty': float("{:.2f}".format(qty)),
                                        'tax': float("{:.2f}".format(tax))
                                    })
                                order_dic.update(
                                    {line.product_id.id: line_dic})
                            if order_dic:
                                for value in order_dic.values():
                                    order_list.append(value)
                if category and order_list:
                    category_order_dic.update(
                        {category.display_name: order_list})

        if not category_order_dic:
            raise UserError(_(
                'There is no Data Found between these dates...'))
        data.update({
            'date_start': data['sh_start_date'],
            'date_end': data['sh_end_date'],
            'category_order_dic': category_order_dic,
        })
        return data

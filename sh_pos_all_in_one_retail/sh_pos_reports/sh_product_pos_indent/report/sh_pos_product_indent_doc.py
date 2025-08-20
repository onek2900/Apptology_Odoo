# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from datetime import timedelta
from pytz import timezone
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class POSProductIndent(models.AbstractModel):
    _name = 'report.sh_pos_all_in_one_retail.sh_pos_product_indent_doc'
    _description = 'Point of Sale product indent report abstract model'

    @api.model
    def _get_report_values(self, docids, data=None):
        data = dict(data or {})
        order_dic = {}
        categories = self.env['product.category'].sudo().browse(
            data.get('sh_category_ids', False))
        partners = self.env['res.partner'].sudo().browse(
            data.get('sh_partner_ids', False))
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
        if partners:
            for partner in partners:
                customer_list = []
                for category in categories:
                    category_dic = {}
                    category_list = []
                    products = self.env['product.product'].sudo().search(
                        [('categ_id', '=', category.id)])
                    for product in products:
                        domain = [
                            ("order_id.date_order", ">=",
                             fields.Datetime.to_string(date_start)),
                            ("order_id.date_order", "<=",
                             fields.Datetime.to_string(date_stop)),
                            ('order_id.partner_id', '=', partner.id),
                            ('product_id', '=', product.id)
                        ]
                        if data.get('sh_status', False) == 'all':
                            domain.append(
                                ('order_id.state', 'not in', ['cancel']))
                        elif data.get('sh_status', False) == 'draft':
                            domain.append(('order_id.state', 'in', ['draft']))
                        elif data.get('sh_status', False) == 'paid':
                            domain.append(('order_id.state', 'in', ['paid']))
                        elif data.get('sh_status', False) == 'done':
                            domain.append(('order_id.state', 'in', ['done']))
                        elif data.get('sh_status', False) == 'invoiced':
                            domain.append(
                                ('order_id.state', 'in', ['invoiced']))
                        if data.get('company_ids', False):
                            domain.append(
                                ('order_id.company_id', 'in', data.get('company_ids', False)))
                        if data.get('sh_session_id', False):
                            domain.append(
                                ('order_id.session_id', '=', data.get('sh_session_id', False)[0]))
                        order_lines = self.env['pos.order.line'].sudo().search(
                            domain).mapped('qty')
                        product_qty = 0.0
                        if order_lines:
                            for qty in order_lines:
                                product_qty += qty
                        if product_qty == 0:
                            continue
                        else:
                            product_dic = {
                                'name': product.display_name,
                                'product_id': product.id,
                                'partner_id': partner.id,
                                'qty': product_qty,
                                'category_id': product.categ_id.id,
                            }
                        category_list.append(product_dic)
                    if category and category_list:
                        category_dic.update({
                            category.display_name: category_list
                        })
                        customer_list.append(category_dic)
                if partner and customer_list:
                    order_dic.update({partner.display_name: customer_list})
        if not order_dic:
            raise UserError(_('There is no Data Found between these dates...'))
        data.update({
            'date_start': data['sh_start_date'],
            'date_end': data['sh_end_date'],
            'order_dic': order_dic,
        })
        return data

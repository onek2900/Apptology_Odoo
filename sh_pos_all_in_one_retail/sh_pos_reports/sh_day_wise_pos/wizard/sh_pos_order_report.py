# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.
from base64 import encodebytes
from datetime import datetime, timedelta
from io import BytesIO
from pytz import utc, timezone
from xlwt import Workbook, easyxf
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT


class POSOrderReport(models.Model):
    _name = 'pos.order.report'
    _description = 'POS Order Report'

    @api.model
    def default_company_ids(self):
        is_allowed_companies = self.env.context.get(
            'allowed_company_ids', False)
        if is_allowed_companies:
            return is_allowed_companies
        return False

    start_date = fields.Datetime(
        "Start Date", required=True, readonly=False, default=fields.Datetime.now)
    end_date = fields.Datetime("End Date", required=True,
                               default=fields.Datetime.now, readonly=False)
    company_ids = fields.Many2many(
        'res.company', string='Companies', default=default_company_ids)
    config_ids = fields.Many2many('pos.config', string="POS Configuration",
                                  required=True, domain="[('company_id', 'in', company_ids)]")

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        if self.filtered(lambda c: c.end_date and c.start_date > c.end_date):
            raise ValidationError(_('start date must be less than end date.'))

    def get_product(self):
        for rec in self:
            if self.start_date:
                date_start = fields.Datetime.from_string(self.start_date)
            else:
                # start by default today 00:00:00
                user_tz = timezone(self.env.context.get(
                    'tz') or self.env.user.tz or 'UTC')
                today = user_tz.localize(fields.Datetime.from_string(
                    fields.Date.context_today(self)))
                date_start = today.astimezone(timezone('UTC'))

            if self.end_date:
                date_stop = fields.Datetime.from_string(self.end_date)
                # avoid a date_stop smaller than date_start
                if date_stop < date_start:
                    date_stop = date_start + timedelta(days=1, seconds=-1)
            else:
                # stop by default today 23:59:59
                date_stop = date_start + timedelta(days=1, seconds=-1)
            product_detail = []
            session_ids = self.env['pos.session'].sudo().search(
                [('config_id', 'in', rec.config_ids.ids)])
            if rec.start_date and rec.end_date:
                if len(rec.company_ids.ids) >= 1:
                    if len(rec.config_ids.ids) >= 1:
                        if len(session_ids.ids) > 0:
                            rec._cr.execute('''select pt.name as product_name,pos.date_order as order_date,pr.id as product_id,
                                sum(pl.qty)::Int  as purchase_cnt
                                from pos_order as pos 
                                left join pos_order_line as pl on pos.id = pl.order_id
                                left join product_product as pr on pr.id = pl.product_id
                                left join product_template as pt on  pr.product_tmpl_id = pt.id
                                where date(date_order) >= date(%s) and date(date_order) <= date(%s) and pos.company_id in %s and pos.session_id in %s and
                                pos.state in ('paid','done','invoiced')
                                group by pt.name,pos.date_order,pr.id
                                ''', (fields.Datetime.to_string(date_start), fields.Datetime.to_string(date_stop), tuple(rec.company_ids.ids), tuple(session_ids.ids)))
                        product_detail = rec._cr.dictfetchall()

                    else:
                        rec._cr.execute('''select pt.name as product_name,
                                            pos.date_order as order_date,pr.id as product_id,
                                             sum(pl.qty)::Int  as purchase_cnt
                                            from pos_order as pos 
                                            left join pos_order_line as pl on pos.id = pl.order_id
                                            left join product_product as pr on pr.id = pl.product_id
                                            left join product_template as pt on  pr.product_tmpl_id = pt.id
                                            where date(date_order) >= date(%s) and date(date_order) <= date(%s) and pos.company_id in %s and 
                                            pos.state in ('paid','done','invoiced')
                                            group by pt.name,pos.date_order,pr.id''', (fields.Datetime.to_string(date_start), fields.Datetime.to_string(date_stop), tuple(rec.company_ids.ids)))

                        product_detail = rec._cr.dictfetchall()
                else:
                    if len(rec.config_ids.ids) >= 1:
                        if len(session_ids.ids) > 0:
                            rec._cr.execute('''select pt.name as product_name,
                                            pos.date_order as order_date,pr.id as product_id,
                                             sum(pl.qty)::Int  as purchase_cnt
                                            from pos_order as pos 
                                            left join pos_order_line as pl on pos.id = pl.order_id
                                            left join product_product as pr on pr.id = pl.product_id
                                            left join product_template as pt on  pr.product_tmpl_id = pt.id
                                            where date(date_order) >= date(%s) and date(date_order) <= date(%s) and pos.session_id in %s and 
                                            pos.state in ('paid','done','invoiced')
                                            group by pt.name,pos.date_order,pr.id''', (fields.Datetime.to_string(date_start), fields.Datetime.to_string(date_stop), tuple(session_ids.ids)))

                        product_detail = rec._cr.dictfetchall()
                    else:
                        rec._cr.execute('''select pt.name as product_name,
                                            pos.date_order as order_date,pr.id as product_id,
                                            sum(pl.qty)::Int  as purchase_cnt
                                            from pos_order as pos 
                                            left join pos_order_line as pl on pos.id = pl.order_id
                                            left join product_product as pr on pr.id = pl.product_id
                                            left join product_template as pt on  pr.product_tmpl_id = pt.id
                                            where date(date_order) >= date(%s) and date(date_order) <= date(%s) and 
                                            pos.state in ('paid','done','invoiced')
                                            group by pt.name,pos.date_order,pr.id''', (fields.Datetime.to_string(date_start), fields.Datetime.to_string(date_stop)))

                        product_detail = rec._cr.dictfetchall()

            output_data = {}
            data_list = []
            final_list = []
            if len(product_detail) > 0:
                current_product = product_detail[0]['product_name']
                last_product = product_detail[-1]['product_name']
                count = 1
                for product_dic in product_detail:
                    if product_dic['product_name'] != current_product:
                        data_list.append(output_data)
                        output_data = {}
                        current_product = product_dic['product_name']
                        output_data['product_id'] = product_dic['product_id']
                        output_data['product'] = current_product
                        output_data['monday'] = None
                        output_data['tuesday'] = None
                        output_data['wednesday'] = None
                        output_data['thursday'] = None
                        output_data['friday'] = None
                        output_data['saturday'] = None
                        output_data['sunday'] = None

                        order_date = product_dic['order_date']
                        if order_date.weekday() == 0:
                            output_data['monday'] = int(
                                product_dic['purchase_cnt'])
                        elif order_date.weekday() == 1:
                            output_data['tuesday'] = int(
                                product_dic['purchase_cnt'])
                        elif order_date.weekday() == 2:
                            output_data['wednesday'] = int(
                                product_dic['purchase_cnt'])
                        elif order_date.weekday() == 3:
                            output_data['thursday'] = int(
                                product_dic['purchase_cnt'])
                        elif order_date.weekday() == 4:
                            output_data['friday'] = int(
                                product_dic['purchase_cnt'])
                        elif order_date.weekday() == 5:
                            output_data['saturday'] = int(
                                product_dic['purchase_cnt'])
                        elif order_date.weekday() == 6:
                            output_data['sunday'] = int(
                                product_dic['purchase_cnt'])
                        if product_dic['product_name'] == last_product:
                            data_list.append(output_data)

                    else:
                        if count == 1:
                            count = 0
                            output_data = {}
                            current_product = product_dic['product_name']
                            output_data['product'] = current_product
                            output_data['product_id'] = product_dic['product_id']
                            order_date = product_dic['order_date']
                            output_data['monday'] = None
                            output_data['tuesday'] = None
                            output_data['wednesday'] = None
                            output_data['thursday'] = None
                            output_data['friday'] = None
                            output_data['saturday'] = None
                            output_data['sunday'] = None

                            if order_date.weekday() == 0:
                                output_data['monday'] = int(
                                    product_dic['purchase_cnt'])
                            elif order_date.weekday() == 1:
                                output_data['tuesday'] = int(
                                    product_dic['purchase_cnt'])
                            elif order_date.weekday() == 2:
                                output_data['wednesday'] = int(
                                    product_dic['purchase_cnt'])
                            elif order_date.weekday() == 3:
                                output_data['thursday'] = int(
                                    product_dic['purchase_cnt'])
                            elif order_date.weekday() == 4:
                                output_data['friday'] = int(
                                    product_dic['purchase_cnt'])
                            elif order_date.weekday() == 5:
                                output_data['saturday'] = int(
                                    product_dic['purchase_cnt'])
                            elif order_date.weekday() == 6:
                                output_data['sunday'] = int(
                                    product_dic['purchase_cnt'])
                        else:
                            output_data['product'] = current_product
                            output_data['product_id'] = product_dic['product_id']
                            order_date = product_dic['order_date']
                            if order_date.weekday() == 0:
                                tmp = output_data['monday'] or 0
                                output_data['monday'] = tmp + \
                                    int(product_dic['purchase_cnt'])
                            elif order_date.weekday() == 1:
                                tmp = output_data['tuesday'] or 0
                                output_data['tuesday'] = tmp + \
                                    int(product_dic['purchase_cnt'])
                            elif order_date.weekday() == 2:
                                tmp = output_data['wednesday'] or 0
                                output_data['wednesday'] = tmp + \
                                    int(product_dic['purchase_cnt'])
                            elif order_date.weekday() == 3:
                                tmp = output_data['thursday'] or 0
                                output_data['thursday'] = tmp + \
                                    int(product_dic['purchase_cnt'])
                            elif order_date.weekday() == 4:
                                tmp = output_data['friday'] or 0
                                output_data['friday'] = tmp + \
                                    int(product_dic['purchase_cnt'])
                            elif order_date.weekday() == 5:
                                tmp = output_data['saturday'] or 0
                                output_data['saturday'] = tmp + \
                                    int(product_dic['purchase_cnt'])
                            elif order_date.weekday() == 6:
                                tmp = output_data['sunday'] or 0
                                output_data['sunday'] = tmp + \
                                    int(product_dic['purchase_cnt'])

                            if product_dic['product_name'] == last_product:
                                data_list.append(output_data)
            if data_list:
                for data in data_list:
                    if data not in final_list:
                        final_list.append(data)
                return final_list
            else:
                return final_list

    def generate_report_data(self):
        data_values = self.get_product()
        if data_values:
            return self.env.ref('sh_pos_all_in_one_retail.action_report_pos_order_day_wise_report').report_action(self)
        else:
            raise UserError(_(
                'There is no Data Found between these dates...'))

    def display_report_data(self):
        data_values = self.get_product()
        self.env['sh.pos.day.wise.report'].search([]).unlink()
        if data_values:
            for record in data_values:
                monday = record.get('monday')
                tuesday = record.get('tuesday')
                wednesday = record.get('wednesday')
                thursday = record.get('thursday')
                friday = record.get('friday')
                saturday = record.get('saturday')
                sunday = record.get('sunday')
                if monday == None:
                    monday = 0
                if tuesday == None:
                    tuesday = 0
                if wednesday == None:
                    wednesday = 0
                if thursday == None:
                    thursday = 0
                if friday == None:
                    friday = 0
                if saturday == None:
                    saturday = 0
                if sunday == None:
                    sunday = 0
                total_value = monday+tuesday+wednesday+thursday+friday+saturday+sunday
                self.env['sh.pos.day.wise.report'].create({
                    'name': record.get('product_id'),
                    'monday': record.get('monday'),
                    'tuesday': record.get('tuesday'),
                    'wednesday': record.get('wednesday'),
                    'thursday': record.get('thursday'),
                    'friday': record.get('friday'),
                    'saturday': record.get('saturday'),
                    'sunday': record.get('sunday'),
                    'total': total_value,
                })
            return {
                'type': 'ir.actions.act_window',
                'name': 'POS Order Day Wise',
                'view_mode': 'tree',
                'res_model': 'sh.pos.day.wise.report',
                'context': "{'create': False,'search_default_group_product': 1}"
            }
        else:
            raise UserError(
                'There is no Data Found between these dates...')

    def print_pos_order_day_wise(self):
        for data in self:
            workbook = Workbook()
            heading_format = easyxf(
                'font:height 300,bold True;pattern: pattern solid, fore_colour gray25;align: horiz center')
            bold = easyxf(
                'font:bold True;pattern: pattern solid, fore_colour gray25;align: horiz left')
            center = easyxf('font:bold True;align: horiz center')
            right = easyxf('font:bold True;align: horiz right')
            row = 1
            if self.start_date:
                date_start = fields.Datetime.from_string(self.start_date)
            else:
                # start by default today 00:00:00
                user_tz = timezone(self.env.context.get(
                    'tz') or self.env.user.tz or 'UTC')
                today = user_tz.localize(fields.Datetime.from_string(
                    fields.Date.context_today(self)))
                date_start = today.astimezone(timezone('UTC'))

            if self.end_date:
                date_stop = fields.Datetime.from_string(self.end_date)
                # avoid a date_stop smaller than date_start
                if date_stop < date_start:
                    date_stop = date_start + timedelta(days=1, seconds=-1)
            else:
                # stop by default today 23:59:59
                date_stop = date_start + timedelta(days=1, seconds=-1)
            user_tz = self.env.user.tz or utc
            local = timezone(user_tz)
            start_date = datetime.strftime(utc.localize(datetime.strptime(str(
                self.start_date), DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local), DEFAULT_SERVER_DATETIME_FORMAT)
            end_date = datetime.strftime(utc.localize(datetime.strptime(str(
                self.end_date), DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(local), DEFAULT_SERVER_DATETIME_FORMAT)
            worksheet = workbook.add_sheet(
                'POS Order Day Wise', cell_overwrite_ok=True)
            worksheet.write_merge(
                0, 1, 0, 8, 'POS Order - Product Sold Day Wise', heading_format)
            worksheet.write_merge(3, 3, 0, 0, "Start Date : ", bold)
            worksheet.write_merge(3, 3, 1, 1, start_date)
            worksheet.write_merge(3, 3, 6, 7, "End Date : ", bold)
            worksheet.write_merge(3, 3, 8, 8, end_date)
            product_detail = []

            if data.start_date and data.end_date:
                session_ids = self.env['pos.session'].sudo().search(
                    [('config_id', 'in', data.config_ids.ids)])
                if len(data.company_ids.ids) >= 1:
                    if len(data.config_ids.ids) >= 1:
                        if len(session_ids.ids) > 0:
                            data._cr.execute('''select pt.name as product_name,
                                            to_char(pos.date_order,'day') as order_date,
                                             sum(pl.qty)::Int  as purchase_cnt
                                            from pos_order as pos 
                                            left join pos_order_line as pl on pos.id = pl.order_id
                                            left join product_product as pr on pr.id = pl.product_id
                                            left join product_template as pt on  pr.product_tmpl_id = pt.id
                                            where date(date_order) >= date(%s) and date(date_order) <= date(%s) and pos.company_id in %s and pos.session_id in %s and
                                            pos.state in ('paid','done','invoiced')
                                            group by pt.name,to_char(pos.date_order,'day')''', (fields.Datetime.to_string(date_start), fields.Datetime.to_string(date_stop), tuple(data.company_ids.ids), tuple(session_ids.ids)))

                        product_detail = data._cr.dictfetchall()
                    else:
                        data._cr.execute('''select pt.name as product_name,
                                            to_char(pos.date_order,'day') as order_date,
                                            sum(pl.qty)::Int  as purchase_cnt
                                            from pos_order as pos 
                                            left join pos_order_line as pl on pos.id = pl.order_id
                                            left join product_product as pr on pr.id = pl.product_id
                                            left join product_template as pt on  pr.product_tmpl_id = pt.id
                                            where date(date_order) >= date(%s) and date(date_order) <= date(%s) and pos.company_id in %s and 
                                            pos.state in ('paid','done','invoiced')
                                            group by pt.name,to_char(pos.date_order,'day')''', (fields.Datetime.to_string(date_start), fields.Datetime.to_string(date_stop), tuple(data.company_ids.ids)))

                        product_detail = data._cr.dictfetchall()
                else:
                    if len(data.config_ids.ids) >= 1:
                        if len(session_ids.ids) > 0:
                            data._cr.execute('''select pt.name as product_name,
                                            to_char(pos.date_order,'day') as order_date,
                                             sum(pl.qty)::Int  as purchase_cnt
                                            from pos_order as pos 
                                            left join pos_order_line as pl on pos.id = pl.order_id
                                            left join product_product as pr on pr.id = pl.product_id
                                            left join product_template as pt on  pr.product_tmpl_id = pt.id
                                            where date(date_order) >= date(%s) and date(date_order) <= date(%s) and pos.session_id in %s and 
                                            pos.state in ('paid','done','invoiced')
                                            group by pt.name,to_char(pos.date_order,'day')''', (fields.Datetime.to_string(date_start), fields.Datetime.to_string(date_stop), tuple(session_ids.ids)))

                        product_detail = data._cr.dictfetchall()
                    else:
                        data._cr.execute('''select pt.name as product_name,
                                            to_char(pos.date_order,'day') as order_date,
                                             sum(pl.qty)::Int  as purchase_cnt
                                            from pos_order as pos 
                                            left join pos_order_line as pl on pos.id = pl.order_id
                                            left join product_product as pr on pr.id = pl.product_id
                                            left join product_template as pt on  pr.product_tmpl_id = pt.id
                                            where date(date_order) >= date(%s) and date(date_order) <= date(%s) and 
                                            pos.state in ('paid','done','invoiced')
                                            group by pt.name,to_char(pos.date_order,'day')''', (fields.Datetime.to_string(date_start), fields.Datetime.to_string(date_stop)))

                        product_detail = data._cr.dictfetchall()
            just_list = []
            final_list = []
            if product_detail:
                for data in product_detail:
                    if data['product_name'] not in just_list:
                        just_list.append(data['product_name'])
                        same_element = list(
                            filter(lambda x: x['product_name'] == data['product_name'], product_detail))
                        normal_list = []
                        final_dic = {}
                        for record in same_element:
                            for final_value in record.values():
                                normal_list.append(final_value)
                        for value in normal_list:
                            if not 'product' in final_dic:
                                final_dic['product'] = value
                                normal_list = list(
                                    filter(lambda a: a != value, normal_list))
                        count = 1
                        for same in normal_list:
                            if count % 2 != 0:
                                final_dic['%s' %
                                          (same.strip())] = normal_list[count]
                            count += 1

                        if 'monday' not in final_dic:
                            final_dic['monday'] = None
                        if 'tuesday' not in final_dic:
                            final_dic['tuesday'] = None
                        if 'wednesday' not in final_dic:
                            final_dic['wednesday'] = None
                        if 'thursday' not in final_dic:
                            final_dic['thursday'] = None
                        if 'friday' not in final_dic:
                            final_dic['friday'] = None
                        if 'saturday' not in final_dic:
                            final_dic['saturday'] = None
                        if 'sunday' not in final_dic:
                            final_dic['sunday'] = None

                        final_list.append(final_dic)
            else:
                raise UserError(
                    'There is no Data Found between these dates...')

            product_detail = final_list
            product = product_detail
            worksheet.col(0).width = int(25*260)
            worksheet.col(1).width = int(14*260)
            worksheet.col(2).width = int(14*260)
            worksheet.col(3).width = int(14*260)
            worksheet.col(4).width = int(14*260)
            worksheet.col(5).width = int(14*260)
            worksheet.col(6).width = int(14*260)
            worksheet.col(7).width = int(14*260)
            worksheet.col(8).width = int(14*260)

            worksheet.write(5, 0, "Product Name", bold)
            worksheet.write(5, 1, "Monday", bold)
            worksheet.write(5, 2, "Tuesday", bold)
            worksheet.write(5, 3, "Wednesday", bold)
            worksheet.write(5, 4, "Thursday", bold)
            worksheet.write(5, 5, "Friday", bold)
            worksheet.write(5, 6, "Saturday", bold)
            worksheet.write(5, 7, "Sunday", bold)
            worksheet.write(5, 8, "Total", bold)
            row = 6
            for p in product:
                # worksheet.write(row, 0, p['product'])
                worksheet.write(row, 0, list(p.get('product').values())[0])
                worksheet.write(row, 1, p['monday'] or 0)
                worksheet.write(row, 2, p['tuesday'] or 0)
                worksheet.write(row, 3, p['wednesday'] or 0)
                worksheet.write(row, 4, p['thursday'] or 0)
                worksheet.write(row, 5, p['friday'] or 0)
                worksheet.write(row, 6, p['saturday'] or 0)
                worksheet.write(row, 7, p['sunday'] or 0)
                total = 0
                if p['monday'] != None:
                    total = total + p['monday']
                if p['tuesday'] != None:
                    total = total + p['tuesday']
                if p['wednesday'] != None:
                    total = total + p['wednesday']
                if p['thursday'] != None:
                    total = total + p['thursday']
                if p['friday'] != None:
                    total = total + p['friday']
                if p['saturday'] != None:
                    total = total + p['saturday']
                if p['sunday'] != None:
                    total = total + p['sunday']
                worksheet.write(row, 8, total)
                row += 1
            row += 1
            worksheet.write(row, 0, "Total", center)
            monday_total = 0
            tuesday_total = 0
            wednesday_total = 0
            thursday_total = 0
            friday_total = 0
            saturday_total = 0
            sunday_total = 0
            for i in product:
                if i['monday'] != None:
                    monday_total = monday_total + i['monday']
                if i['tuesday']:
                    tuesday_total = tuesday_total + i['tuesday']
                if i['wednesday']:
                    wednesday_total = wednesday_total + i['wednesday']
                if i['thursday']:
                    thursday_total = thursday_total + i['thursday']
                if i['friday']:
                    friday_total = friday_total + i['friday']
                if i['saturday']:
                    saturday_total = saturday_total + i['saturday']
                if i['sunday']:
                    sunday_total = sunday_total + i['sunday']
            worksheet.write(row, 1, monday_total, right)
            worksheet.write(row, 2, tuesday_total, right)
            worksheet.write(row, 3, wednesday_total, right)
            worksheet.write(row, 4, thursday_total, right)
            worksheet.write(row, 5, friday_total, right)
            worksheet.write(row, 6, saturday_total, right)
            worksheet.write(row, 7, sunday_total, right)
            total = monday_total+tuesday_total+wednesday_total + \
                thursday_total+friday_total+saturday_total+sunday_total
            worksheet.write(row, 8, total, right)

            filename = 'POS Order Day Wise Xls Report.xls'
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

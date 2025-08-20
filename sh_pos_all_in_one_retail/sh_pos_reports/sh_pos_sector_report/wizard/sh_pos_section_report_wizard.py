# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from base64 import encodebytes
from datetime import datetime, date, timedelta
from io import BytesIO
from math import ceil
from pytz import timezone
from xlwt import easyxf, Workbook, XFStyle, Font, Borders
from odoo import models, fields, _
from odoo.exceptions import UserError


class SectionReportWizard(models.TransientModel):
    _name = 'sh.pos.section.report.wizard'
    _description = "POS section Report wizard"

    date = fields.Date(default=date.today(), required=True)
    state = fields.Selection(
        [('draft', 'New'), ('cancel', 'Cancelled'), ('paid', 'Paid'),
         ('done', 'Posted'), ('invoiced', 'Invoiced')],
        'Status', required=True, default='done')

    pos_config_ids = fields.Many2many('pos.config', string="POS Configuration")

    user_ids = fields.Many2many('res.users', string="Users")
    total_weeks = fields.Integer(
        string="Total Weeks", required=True, default=9)
    company_id = fields.Many2one(
        'res.company', default=lambda self: self.env.company)

    def print_section_report(self):
        if self.total_weeks < 1:
            raise UserError(_(
                "Please select atleast 1 week to print the report!!"))

        workbook = Workbook()

        # normal_record = xlwt.easyxf('font:height 210;align: vert center')

        header_record = easyxf(
            'font:height 300;align: horiz left;align: vert center;font:bold True')
        # only_bold = xlwt.easyxf('font:bold True;' "borders: top thin,bottom thin,right thin,left thin")
        bold_center = easyxf(
            'align: horiz center;font:bold True;' "borders: top thin,bottom thin,right thin,left thin")
        right_side = easyxf(
            'align: horiz right;' "borders: top thin,bottom thin,right thin,left thin")
        left_side = easyxf(
            'align: horiz left;' "borders: top thin,bottom thin,right thin,left thin")
        left_bold = easyxf(
            'align: horiz left;font:bold True;' "borders: top thin,bottom thin,right thin,left thin")
        right_bold = easyxf(
            'align: horiz right;font:bold True;' "borders: top thin,bottom thin,right thin,left thin")

        currency_style = XFStyle()
        font = Font()
        font.bold = True
        currency_style.font = font

        # borders
        borders = Borders()
        borders.bottom = 1
        borders.top = 1
        borders.left = 1
        borders.right = 1
        currency_style.borders = borders

        # currency_style.num_format_str = "[$$-409]#,##0.00;-[$$-409]#,##0.00"
        currency_style.num_format_str = str(
            self.company_id.currency_id.symbol)+"#,##0.00;"

        currency_style_sided = XFStyle()
        # borders
        borders = Borders()
        borders.bottom = 1
        borders.top = 1
        borders.left = 1
        borders.right = 1
        currency_style_sided.borders = borders

        # currency_style_sided.num_format_str = "[$$-409]#,##0.00;-[$$-409]#,##0.00"
        currency_style_sided.num_format_str = str(
            self.company_id.currency_id.symbol)+"#,##0.00;"

        worksheet = workbook.add_sheet('Sheet 1', bold_center)

        today = self.date
        # week_no = today.isocalendar()[1]

        first_day = (today - timedelta(days=today.weekday())) - \
            timedelta(days=7 * (self.total_weeks - 1))

        self.env.cr.execute(
            """select name,from_time,to_time from sh_pos_sector order by sequence;""")
        res = self.env.cr.fetchall()

        # target_week_no = first_day.isocalendar()[1] - 8 # week number before 2 months
        row = 1
        # print("\n\n\n\n\nfirst day",first_day.isocalendar())
        date_wise_total = {}
        if (self.total_weeks % 2) == 0:
            range_value = self.total_weeks / 2
        else:
            range_value = (self.total_weeks + 1) / 2
        report_start_date = ''
        report_end_date = ''
        for week_count in range(int(range_value)):
            row += 2
            # current_week_no = target_week_no + (week_count *2)
            # first_day = datetime.datetime.strptime(f'{int(today.year)}-W{int(current_week_no)}-1', "%Y-W%W-%w").date()
            day = first_day
            # day_week_end = first_day + timedelta(days=6)

            weekly_total = {}

            week_total_list = []
            week_total_list.append('')  # Total Row
            weekly_total['init'] = ['Date']
            count = 0

            final_total = 0.0  # Final week 1 total

            # Start====== column wise total week 1
            monday_total = 0.0
            tuesday_total = 0.0
            web_total = 0.0
            thur_total = 0.0
            fri_total = 0.0
            sat_total = 0.0
            sun_total = 0.0
            # ENd ====== column wise total week 1

            final_total1 = 0.0  # Final week 2 total

            # Start====== column wise total week 2
            monday_total1 = 0.0
            tuesday_total1 = 0.0
            web_total1 = 0.0
            thur_total1 = 0.0
            fri_total1 = 0.0
            sat_total1 = 0.0
            sun_total1 = 0.0
            # ENd ====== column wise total week 2

            # start =============if last week then print only 1 week record
            if week_count == (range_value - 1) and (self.total_weeks % 2) != 0:
                display_week_no = 7
            else:
                display_week_no = 14

            for sector in res:

                date_sector_data = []
                date_sector_data.append(sector[0])
                total = 0.0  # week 1- sector wise total
                total1 = 0.0  # week 2 - sector wise total

                from_time = '{0:02.0f}:{1:02.0f}:00'.format(
                    *divmod((sector[1]) * 60, 60))
                to_time = '{0:02.0f}:{1:02.0f}:59'.format(
                    *divmod((sector[2]) * 60, 60))
                for i in range(display_week_no):
                    day = first_day + timedelta(days=i)
                    day_total = 0.0
                    if week_count == 0 and i == 0:
                        report_start_date = day.strftime("%Y-%m-%d")
                    if week_count == (range_value - 1):
                        report_end_date = day.strftime("%Y-%m-%d")

                    day_start = day.strftime("%Y-%m-%d "+from_time)
                    day_end = day.strftime("%Y-%m-%d "+to_time)
                    user_tz = timezone(self.env.context.get(
                        'tz') or self.env.user.tz or 'UTC')
                    day_start_day = user_tz.localize(
                        fields.Datetime.from_string(day_start))
                    date_start = day_start_day.astimezone(timezone('UTC'))
                    day_start = fields.Datetime.to_string(date_start)

                    user_tz = timezone(self.env.context.get(
                        'tz') or self.env.user.tz or 'UTC')
                    day_end_day = user_tz.localize(
                        fields.Datetime.from_string(day_end))
                    date_end = day_end_day.astimezone(timezone('UTC'))
                    day_end = fields.Datetime.to_string(date_end)

                    # users
                    user_list = []
                    if self.user_ids:
                        user_list.extend(self.user_ids.ids)

                    else:
                        users = self.env['res.users'].search([])
                        user_list = users.ids

                    if len(user_list) == 1:
                        listt = [(tuple(user_list))]
                        user_list = ', '.join(
                            '({})'.format(t[0]) for t in listt)

                    else:
                        user_list = tuple(user_list)

                    # Pos config
                    pos_config_list = []
                    if self.pos_config_ids:
                        pos_config_list.extend(self.pos_config_ids.ids)

                    else:
                        pos_configs = self.env['pos.config'].search([])
                        pos_config_list = pos_configs.ids

                    if len(pos_config_list) == 1:
                        listt = [(tuple(pos_config_list))]
                        pos_config_list = ', '.join(
                            '({})'.format(t[0]) for t in listt)

                    else:
                        pos_config_list = tuple(pos_config_list)

                    self.env.cr.execute(""" select ROUND(sum(o.amount_total),2) from pos_order as o
                                            LEFT JOIN pos_session as ps ON ps.id = o.session_id 
                                            LEFT JOIN pos_config as pcf ON pcf.id = ps.config_id 
                                            where  o.state = '%s' and o.user_id in %s and pcf.id in %s and date_order> '%s' 
                                            and date_order<= '%s'; """ % (self.state, user_list, pos_config_list, day_start, day_end))

                    day_wise_total = self.env.cr.fetchall()

                    if count == 0:  # for header row of dates
                        tmp_list = weekly_total['init']
                        tmp_list.append(day.strftime("%d/%m/%Y"))
                        # add weekly total after sunday
                        if i == 6 or i == 13:
                            tmp_list.append('Weekly Total')

                        weekly_total['init'] = tmp_list

                    if day_wise_total[0][0]:
                        if i < 7:
                            total += day_wise_total[0][0]
                        else:
                            total1 += day_wise_total[0][0]
                        day_total += day_wise_total[0][0]

                    if i < 7:
                        final_total += day_total
                    else:

                        final_total1 += day_total

                    if i == 0:
                        monday_total += day_total
                        date_sector_data.append(day_total)
                    elif i == 1:
                        tuesday_total += day_total
                        date_sector_data.append(day_total)
                    elif i == 2:
                        web_total += day_total
                        date_sector_data.append(day_total)
                    elif i == 3:
                        thur_total += day_total
                        date_sector_data.append(day_total)
                    elif i == 4:
                        fri_total += day_total
                        date_sector_data.append(day_total)
                    elif i == 5:
                        sat_total += day_total
                        date_sector_data.append(day_total)
                    elif i == 6:
                        sun_total += day_total
                        date_sector_data.append(day_total)
                        date_sector_data.append(total)
                    elif i == 7:
                        monday_total1 += day_total
                        date_sector_data.append(day_total)
                    elif i == 8:
                        tuesday_total1 += day_total
                        date_sector_data.append(day_total)
                    elif i == 9:
                        web_total1 += day_total
                        date_sector_data.append(day_total)
                    elif i == 10:
                        thur_total1 += day_total
                        date_sector_data.append(day_total)
                    elif i == 11:
                        fri_total1 += day_total
                        date_sector_data.append(day_total)
                    elif i == 12:
                        sat_total1 += day_total
                        date_sector_data.append(day_total)
                    elif i == 13:
                        sun_total1 += day_total
                        date_sector_data.append(day_total)
                        date_sector_data.append(total1)

                count = 1
                weekly_total[sector[0]] = date_sector_data
            # END ==== sector wise list prepare

            week_total_list.append(monday_total)
            week_total_list.append(tuesday_total)
            week_total_list.append(web_total)
            week_total_list.append(thur_total)
            week_total_list.append(fri_total)
            week_total_list.append(sat_total)
            week_total_list.append(sun_total)
            week_total_list.append(final_total)

            # skip print in case of current week there is only 1 week
            if week_count != (range_value - 1) or (self.total_weeks % 2) == 0:
                week_total_list.append(monday_total1)
                week_total_list.append(tuesday_total1)
                week_total_list.append(web_total1)
                week_total_list.append(thur_total1)
                week_total_list.append(fri_total1)
                week_total_list.append(sat_total1)
                week_total_list.append(sun_total1)
                week_total_list.append(final_total1)

            weekly_total['total'] = week_total_list

            if week_count == (range_value - 1) and (self.total_weeks % 2) != 0:
                first_day = first_day + timedelta(days=7)
            else:
                first_day = first_day + timedelta(days=14)

            date_list = weekly_total.get('init')
            total_list = weekly_total.get('total')
            date_total_dict = dict(zip(date_list, total_list))
            date_wise_total.update(date_total_dict)

            col = 0
            for key, value in weekly_total.items():
                col = 0
                for x in value:
                    if key == 'init':
                        if x == 0:
                            worksheet.col(col).width = 3000
                            worksheet.write(row, col, '-', left_bold)
                        else:
                            worksheet.col(col).width = 3000
                            if col == 0:
                                worksheet.write(row, col, x, left_bold)
                            else:
                                worksheet.write(row, col, x, bold_center)
                    elif key == 'total':
                        if x == 0:
                            worksheet.col(col).width = 3000
                            worksheet.write(row, col, '-', right_bold)
                        else:
                            worksheet.col(col).width = 3000
                            if col == 0:
                                worksheet.write(row, col, x, right_side)
                            else:
                                worksheet.write(row, col, x, currency_style)
                    else:
                        if x == 0:
                            if col == 0:
                                worksheet.col(col).width = 3000
                                worksheet.write(row, col, '-', left_side)
                            else:
                                worksheet.col(col).width = 3000
                                worksheet.write(row, col, '-', right_side)
                        else:
                            if col == 0:
                                worksheet.col(col).width = 3000
                                worksheet.write(row, col, x, left_side)
                            else:
                                worksheet.col(col).width = 3000
                                worksheet.write(
                                    row, col, x, currency_style_sided)
                    col += 1
                    if col == 9:
                        col += 1
                row += 1

        worksheet.write_merge(0, 1, 0, 7, 'Sector Wise POS Report ('+str(
            report_start_date)+' to '+str(report_end_date)+')', header_record)
        worksheet.write_merge(0, 1, 9, 10, 'Status : ' + dict(
            self._fields['state'].selection).get(self.state), header_record)

        listToStr = ''
        if self.user_ids:
            listToStr = ', '.join([str(elem)
                                  for elem in self.user_ids.mapped('name')])

            worksheet.write_merge(
                0, 1, 11, 14, 'Users : ' + listToStr, header_record)

        if 'Date' in date_wise_total:
            del date_wise_total['Date']

        if 'Weekly Total' in date_wise_total:
            del date_wise_total['Weekly Total']

        month_week_total = {}

        for key, value in date_wise_total.items():
            day = datetime.strptime(key, '%d/%m/%Y')
            month_key = datetime.strftime(day, '%b %y')

            first_day = day.replace(day=1)
            dom = day.day
            adjusted_dom = dom + first_day.weekday()
            week_no = int(ceil(adjusted_dom/7.0))
            if month_key in month_week_total:
                temp_dict = month_week_total[month_key]
                if week_no in temp_dict:
                    temp_total = temp_dict[week_no]
                    temp_dict[week_no] = temp_total + value
                else:
                    temp_dict[week_no] = value

            else:
                month_week_total[month_key] = {week_no: value}

        row = 5
        col = 21
        for key, value in month_week_total.items():
            week_total = 0.0
            for week_no, data in value.items():
                col = 21
                worksheet.write(row, col, data, currency_style_sided)
                col += 2
                if week_no == 1:
                    worksheet.write(row, col, str("First Week"), left_side)
                elif week_no == 2:
                    worksheet.write(row, col, str("2nd Week"), left_side)
                elif week_no == 3:
                    worksheet.write(row, col, str("3rd Week"), left_side)
                elif week_no == 4:
                    worksheet.write(row, col, str("4th Week"), left_side)
                elif week_no == 5:
                    worksheet.write(row, col, str("5th Week"), left_side)
                elif week_no == 6:
                    worksheet.write(row, col, str("6th Week"), left_side)
                row += 1
                week_total += data

            col = 19

            worksheet.write_merge(row, row, col, col+1,
                                  str(key)+' Total Sale', right_bold)
            col += 2
            worksheet.write(row, col, week_total, currency_style)
            row += 5

        filename = 'Sector Weekly Report.xls'
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

        url = "/web/content/" + str(attachment.id) + "?download=true"
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }

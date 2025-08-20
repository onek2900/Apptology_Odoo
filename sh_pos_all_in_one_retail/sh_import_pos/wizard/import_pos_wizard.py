# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields, models, _
from odoo.exceptions import UserError
import datetime
import csv
import base64
import xlrd
import pytz
from odoo.tools import ustr
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class ImportPosWizard(models.TransientModel):
    _name = "import.pos.wizard"
    _description = "Import POS Order Wizard"

    import_type = fields.Selection([
        ('csv', 'CSV File'),
        ('excel', 'Excel File')
    ], default="csv", string="Import File Type", required=True)
    file = fields.Binary(string="File", required=True)
    product_by = fields.Selection([
        ('name', 'Name'),
        ('int_ref', 'Internal Reference'),
        ('barcode', 'Barcode')
    ], default="name", string="Product By", required=True)
    is_create_customer = fields.Boolean(string="Create Customer?")
    order_no_type = fields.Selection([
        ('auto', 'Auto'),
        ('as_per_sheet', 'As per sheet')
    ], default="auto", string="POS Order Number", required=True)
    sh_partner_by = fields.Selection([
        ('name', 'Name'),
        ('ref', 'Reference'),
        ('id', 'ID')
    ], default="name", string="Customer By")

    def show_success_msg(self, counter, confirm_rec, skipped_line_no):

        # to close the current active wizard
        action = self.env.ref('sh_pos_all_in_one_retail.sh_import_pos_action').read()[0]
        action = {'type': 'ir.actions.act_window_close'}

        # open the new success message box
        view = self.env.ref('sh_pos_all_in_one_retail.sh_message_wizard')
        view_id = view and view.id or False
        context = dict(self._context or {})
        dic_msg = str(counter) + " Records imported successfully \n"
        dic_msg = dic_msg + str(confirm_rec) + " Records Confirm"
        if skipped_line_no:
            dic_msg = dic_msg + "\nNote:"
        for k, v in skipped_line_no.items():
            dic_msg = dic_msg + "\nRow No " + k + " " + v + " "
        context['message'] = dic_msg

        return {
            'name': 'Success',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sh.message.wizard',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': context,
        }

    
    def read_xls_book(self):
        book = xlrd.open_workbook(file_contents=base64.decodebytes(self.file))
        sheet = book.sheet_by_index(0)
        # emulate Sheet.get_rows for pre-0.9.4
        values_sheet = []
        for rowx, row in enumerate(map(sheet.row, range(sheet.nrows)), 1):
            values = []
            for colx, cell in enumerate(row, 1):
                if cell.ctype is xlrd.XL_CELL_NUMBER:
                    is_float = cell.value % 1 != 0.0
                    values.append(
                        str(cell.value) if is_float else str(int(cell.value)))
                elif cell.ctype is xlrd.XL_CELL_DATE:
                    is_datetime = cell.value % 1 != 0.0
                    # emulate xldate_as_datetime for pre-0.9.3
                    dt = datetime.datetime(*xlrd.xldate.xldate_as_tuple(
                        cell.value, book.datemode))
                    values.append(
                        dt.strftime(DEFAULT_SERVER_DATETIME_FORMAT
                                    ) if is_datetime else dt.
                        strftime(DEFAULT_SERVER_DATE_FORMAT))
                elif cell.ctype is xlrd.XL_CELL_BOOLEAN:
                    values.append(u'True' if cell.value else u'False')
                elif cell.ctype is xlrd.XL_CELL_ERROR:
                    raise ValueError(
                        _("Invalid cell value at row %(row)s, column %(col)s: %(cell_value)s"
                          ) % {
                              'row':
                              rowx,
                              'col':
                              colx,
                              'cell_value':
                              xlrd.error_text_from_code.get(
                                  cell.value,
                                  _("unknown error code %s") % cell.value)
                        })
                else:
                    values.append(cell.value)
            values_sheet.append(values)
        return values_sheet


    def import_pos_apply(self):
        pos_line_obj = self.env['pos.order.line']
        pos_order_obj = self.env['pos.order']
        # perform import lead
        if self and self.file:
                # For CSV
                if self.import_type == 'csv' or self.import_type == 'excel':
                    for rec in self:
                        counter = 1
                        skipped_line_no = {}
                        # row_field_dic = {}
                        # row_field_error_dic = {}
                    try:
                        values = []
                        created_pos_list_for_confirm = []
                        created_pos_list = []
                        running_pos = ''
                        if self.import_type == 'csv':

                            file = str(
                                    base64.decodebytes(self.file).decode('utf-8'))
                            values = csv.reader(file.splitlines())
                            skip_header = True                            
                            created_pos = False
                            
                        elif self.import_type == 'excel':
                            values = self.read_xls_book()
                            # print('\n\n\n ---- EXCEL ---- ', self.import_type,'---- \n\n\n')
                        skip_header = True

                        for row in values:
                            try:
                                if skip_header:
                                    skip_header = False
                                    counter = counter + 1
                                    continue

                                if row[0] not in (None, "") and row[5] not in (None, ""):
                                    vals = {}
                                    print('\n\n\n -------- ',row[0],'-------- \n\n\n')
                                    if row[0] != '':
                                        tamp=running_pos
                                        print('\n\n\n -------- if ',row[0],'-------- \n\n\n')
                                        running_pos = row[0]
                                        pos_vals = {}
                                        domain = []

                                        if row[1] not in (None, ""):
                                            search_session = self.env['pos.session'].search(
                                                [('name', '=', row[1])], limit=1)
                                            if search_session:
                                                pos_vals.update(
                                                    {'session_id': search_session.id})
                                            else:
                                                skipped_line_no[str(
                                                    counter)] = " - Session not found. "
                                                counter = counter + 1
                                                continue

                                        if row[2] not in (None, ""):
                                            partner_obj = self.env["res.partner"]

                                            if self.sh_partner_by == 'name':
                                                domain += [('name',
                                                            '=', row[2])]
                                            if self.sh_partner_by == 'ref':
                                                domain += [('ref',
                                                            '=', row[2])]
                                            if self.sh_partner_by == 'id':
                                                domain += [('id', '=', row[2])]
                                            partner = partner_obj.search(
                                                domain, limit=1)

                                            if partner:
                                                pos_vals.update(
                                                    {'partner_id': partner.id})
                                            elif rec.is_create_customer:
                                                partner = partner_obj.create({'company_type': 'person',
                                                                              'name': row[2],
                                                                              })
                                                if not partner:
                                                    skipped_line_no[str(
                                                        counter)] = " - Customer not created. "
                                                    counter = counter + 1
                                                    continue
                                                else:
                                                    pos_vals.update(
                                                        {'partner_id': partner.id})
                                            else:
                                                pos_vals.update({'partner_id': False})
                                        else:
                                            pos_vals.update({'partner_id': False})

                                        if row[3] not in (None, ""):
                                            cd = row[3]
                                            user_tz = pytz.timezone(self.env.user.tz or self.env.context.get('tz') or 'UTC')
                                            dt = user_tz.localize(fields.Datetime.from_string(cd)).astimezone(pytz.timezone('UTC'))

                                            pos_vals.update({'date_order': fields.Datetime.to_string(dt)})

                                        if row[4] not in (None, ""):
                                            search_user = self.env['res.users'].search(
                                                [('name', '=', row[4])], limit=1)
                                            if search_user:
                                                pos_vals.update(
                                                    {'user_id': search_user.id})
                                            else:
                                                skipped_line_no[str(
                                                    counter)] = " - User not found. "
                                                counter = counter + 1
                                                continue
                                        pos_vals.update({'amount_tax': 0.0})
                                        pos_vals.update({'amount_total': 0.0})
                                        pos_vals.update(
                                            {'company_id': self.env.user.company_id.id})
                                        pos_vals.update({'amount_paid': 0.0})
                                        pos_vals.update({'amount_return': 0.0})
                                        if rec.order_no_type == 'as_per_sheet':
                                            pos_vals.update({"name": row[0]})
                                        created_pos = pos_order_obj.create(
                                            pos_vals)
                                        created_pos._onchange_amount_all()
                                        created_pos._compute_batch_amount_all()
                                        created_pos_list_for_confirm.append(
                                            created_pos.id)
                                        created_pos_list.append(created_pos.id)

                                    if created_pos:

                                        field_nm = 'name'
                                        if rec.product_by == 'name':
                                            field_nm = 'name'
                                        elif rec.product_by == 'int_ref':
                                            field_nm = 'default_code'
                                        elif rec.product_by == 'barcode':
                                            field_nm = 'barcode'

                                        search_product = self.env['product.product'].search(
                                            [(field_nm, '=', row[5])], limit=1)
                                        if search_product:
                                            vals.update(
                                                {'product_id': search_product.id,
                                                 'full_product_name': search_product.display_name})

                                            if row[6] != '':
                                                vals.update({'name': row[6]})

                                            if row[7] != '':
                                                vals.update({'qty': row[7]})
                                            else:
                                                vals.update({'qty': 1})

                                            if row[8] in (None, "") and search_product.uom_id:
                                                vals.update(
                                                    {'product_uom_id': search_product.uom_id.id})
                                            else:
                                                search_uom = self.env['uom.uom'].search(
                                                    [('name', '=', row[8])], limit=1)
                                                if search_uom:
                                                    vals.update(
                                                        {'product_uom_id': search_uom.id})
                                                else:
                                                    skipped_line_no[str(
                                                        counter)] = " - Unit of Measure not found. "
                                                    counter = counter + 1
                                                    if created_pos.id in created_pos_list_for_confirm:
                                                        created_pos_list_for_confirm.remove(
                                                            created_pos.id)
                                                    continue

                                            if row[9] in (None, ""):
                                                vals.update(
                                                    {'price_unit': search_product.lst_price})
                                            else:
                                                vals.update(
                                                    {'price_unit': row[9]})

                                            if row[10].strip() in (None, "") and search_product.taxes_id:
                                                vals.update(
                                                    {'tax_ids': [(6, 0, search_product.taxes_id.ids)]})
                                            else:
                                                taxes_list = []
                                                some_taxes_not_found = False
                                                for x in row[10].split(','):
                                                    x = x.strip()
                                                    if x != '':
                                                        search_tax = self.env['account.tax'].search(
                                                            [('name', '=', x)], limit=1)
                                                        if search_tax:
                                                            taxes_list.append(
                                                                search_tax.id)
                                                        else:
                                                            some_taxes_not_found = True
                                                            skipped_line_no[str(
                                                                counter)] = " - Taxes " + x + " not found. "
                                                            break
                                                if some_taxes_not_found:
                                                    counter = counter + 1
                                                    if created_pos.id in created_pos_list_for_confirm:
                                                        created_pos_list_for_confirm.remove(
                                                            created_pos.id)
                                                    continue
                                                else:
                                                    if taxes_list:
                                                        vals.update(
                                                            {'tax_ids': [(6, 0, taxes_list)]})
                                                    else:
                                                        vals.update(
                                                            {'tax_ids': [(6, 0, '')]})
                                            price_subtotal = float(float(row[9]))
                                            price_subtotal_incl = float(float(row[9]))
                                            if vals.get('tax_ids', False):
                                                if vals.get('tax_ids')[0] and vals.get('tax_ids')[0][2] not in (None, ''):
                                                    taxObj = self.env['account.tax'].search([('id', 'in', vals.get('tax_ids')[0][2])])
                                                    compute_tax = taxObj.compute_all(float(row[9]), product=search_product.product_tmpl_id, partner=self.env['res.partner'])
                                                    price_subtotal = compute_tax['total_excluded']
                                                    price_subtotal_incl = compute_tax['total_included']

                                            vals.update({'price_subtotal': float(price_subtotal) * float(row[7]), 'price_subtotal_incl':price_subtotal_incl * float(row[7])})
                                            vals.update(
                                                {'order_id': created_pos.id})
                                            line = pos_line_obj.create(vals)

                                            line.order_id._compute_batch_amount_all()
                                            line.order_id._onchange_amount_all()
                                            line.order_id._compute_order_name()

                                            counter = counter + 1

                                        else:
                                            skipped_line_no[str(
                                                counter)] = " - Product not found. "
                                            counter = counter + 1
                                            if created_pos.id in created_pos_list_for_confirm:
                                                created_pos_list_for_confirm.remove(
                                                    created_pos.id)
                                            continue

                                    else:
                                        skipped_line_no[str(
                                            counter)] = " - Order not created. "
                                        counter = counter + 1
                                        continue

                                else:
                                    skipped_line_no[str(
                                        counter)] = " - POS Order or Product field is empty. "
                                    counter = counter + 1

                            except Exception as e:
                                skipped_line_no[str(
                                    counter)] = " - Value is not valid " + ustr(e)
                                counter = counter + 1
                                continue

                    except Exception as e:
                        raise UserError(
                            _("Sorry, Your csv file does not match with our format " + ustr(e)))

                    if counter > 1:
                        completed_records = len(created_pos_list)
                        confirm_rec = len(created_pos_list_for_confirm)
                        res = self.show_success_msg(
                            completed_records, confirm_rec, skipped_line_no)
                        return res

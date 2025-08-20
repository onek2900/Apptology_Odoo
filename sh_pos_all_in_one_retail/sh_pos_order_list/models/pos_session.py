# Copyright (C) Softhealer Technologies.
# Part of Softhealer Technologies.

from odoo import models, fields
from datetime import datetime, timedelta


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _pos_data_process(self, loaded_data):
        super()._pos_data_process(loaded_data)

        if self.config_id and self.config_id.sh_enable_order_list:
            # load all order lines
            lines = self.load_all_pos_order_lines()
            loaded_data['pos_order_line_by_id'] = {
                line['id']: line for line in lines}

            if self.config_id.sh_load_order_by == "all":
                orders = self.load_all_pos_orders()
                loaded_data['pos_order_by_id'] = {order['id']: [order, list(
                    filter(lambda x: x.get('order_id') == order['id'], lines))] for order in orders}
            elif self.config_id.sh_load_order_by == "session_wise":
                # Load session wise orders
                orders = self.load_session_wise_pos_orders()
                loaded_data['pos_order_by_id'] = {order['id']: [order, list(
                    filter(lambda x: x.get('order_id') == order['id'], lines))] for order in orders}
            elif self.config_id.sh_load_order_by == "day_wise":
                orders = self.load_day_wise_pos_orders()
                loaded_data['pos_order_by_id'] = {order['id']: [order, list(
                    filter(lambda x: x.get('order_id') == order['id'], lines))] for order in orders}

    def load_day_wise_pos_orders(self):
        field_list = self.get_order_fields()
        table_fields = ','.join(field_list)

        if self.config_id.sh_day_wise_option == "current_day":
            start_date = fields.Date.today()
            daystart = datetime(year=start_date.year, month=start_date.month,
                                day=start_date.day, hour=0, minute=0, second=0)
            dayend = datetime(year=start_date.year, month=start_date.month,
                              day=start_date.day, hour=23, minute=59, second=59)

        elif self.config_id.sh_day_wise_option == "last_no_day":

            start_date = fields.Date.today()
            previus_day = start_date - \
                timedelta(days=self.config_id.sh_last_no_days - 1)

            daystart = datetime(year=previus_day.year, month=previus_day.month,
                                day=previus_day.day, hour=0, minute=0, second=0)
            dayend = datetime(year=start_date.year, month=start_date.month,
                              day=start_date.day, hour=23, minute=59, second=59)

        if daystart and dayend:
            self.env.cr.execute(f""" SELECT {table_fields} FROM pos_order pos_order
                            LEFT OUTER JOIN res_partner partner ON partner.id = pos_order.partner_id 
                            JOIN pos_order_line ol on ol.order_id = pos_order.id
                            WHERE pos_order.company_id = {self.env.company.id}
                            AND pos_order.date_order >= %(start_date)s
                            AND pos_order.date_order <= %(end_date)s
                            """, {
                                'start_date': daystart,
                                'end_date': dayend
                                })
            orders = self.env.cr.dictfetchall()

        if orders:
            return orders
        else:
            return []

    def load_session_wise_pos_orders(self):
        field_list = self.get_order_fields()
        table_fields = ','.join(field_list)

        if self.config_id.sh_session_wise_option == "current_session":
            # Give only currunt session id
            session_ids = [self.id]
        elif self.config_id.sh_session_wise_option == "last_no_session":
            # take only last numner of session based on configuration
            session_query = f""" SELECT pos_session.id FROM pos_session
                                JOIN pos_config pc ON pc.id = pos_session.config_id
                                WHERE pc.company_id = {self.env.company.id} 
                                ORDER BY pos_session.id DESC
                                LIMIT {self.config_id.sh_last_no_session} """
            self.env.cr.execute(session_query)
            query_session_ids = self.env.cr.dictfetchall()
            # Take session id list from pos_session table
            if query_session_ids:
                session_ids = list(
                    map(lambda x: x.get('id'), query_session_ids))
        else:
            session_ids = []

        if session_ids:
            self.env.cr.execute(f""" SELECT {table_fields} FROM pos_order pos_order
                                LEFT OUTER JOIN res_partner partner ON partner.id = pos_order.partner_id 
                                JOIN pos_session ps ON ps.id = pos_order.session_id
                                WHERE pos_order.company_id = %(company_id)s
                                AND pos_order.session_id IN %(sh_session)s """, {
                'company_id': self.env.company.id,
                'sh_session': tuple(session_ids),
            })
            query_data = self.env.cr.dictfetchall()
        else:
            query_data = False

        if query_data:
            orders = query_data
        else:
            orders = []

        return orders

    def get_order_fields(self):
        return ['pos_order.id', 'pos_order.name', 'pos_order.date_order', 'pos_order.partner_id', 'pos_order.pos_reference', 'pos_order.amount_total', 'pos_order.state', 'partner.name as partner_name']

    def load_all_pos_orders(self):
        field_list = self.get_order_fields()
        table_fields = ','.join(field_list)

        self.env.cr.execute(f""" SELECT {table_fields} FROM pos_order pos_order
                            LEFT OUTER JOIN res_partner partner ON partner.id = pos_order.partner_id 
                            JOIN pos_order_line ol on ol.order_id = pos_order.id
                            WHERE pos_order.company_id = {self.env.company.id}
                            """)
        orders = self.env.cr.dictfetchall()

        return orders

    # def load_all_pos_order_lines(self):
    #     self.env.cr.execute(""" SELECT  ol.product_id,ol.id ,ol.qty ,ol.price_unit, ol.discount, ol.price_subtotal,ol.order_id, ol.price_subtotal_incl, ol.add_section FROM pos_order_line ol
    #                         INNER JOIN pos_order pos ON (pos.id=ol.order_id)
    #                         """)
    #     lines = self.env.cr.dictfetchall()
    #     return lines

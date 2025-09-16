# -*- coding: utf-8 -*-
import logging
import requests
import re
import os
from datetime import timedelta
from odoo import api, fields, models
from odoo.modules.module import get_resource_path

_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    """Inherit class to add new fields and functions"""
    _inherit = "pos.order"

    order_type = fields.Selection([
        ('1', 'Pick up'),
        ('2', 'Delivery'),
        ('3', 'Eat-In'),       
    ], string='Order Type', help='Type of deliverect order')
    order_payment_type = fields.Selection([
        ('0', 'Credit Card'),
        ('1', 'Cash'),
        ('2', 'On Delivery'),
        ('3', 'Online'),
        ('4', 'Credit Card at door'),
        ('5', 'Pin at Door'),
        ('6', 'Voucher at Door'),
        ('7', 'Meal Voucher'),
        ('8', 'Bank Contact'),
        ('9', 'Other'),
    ], string='Payment Method', help='type of payment method used for deliverect order')
    online_order_id = fields.Char(string='Online Order ID', help='online order id provided by deliverect')
    online_order_paid = fields.Boolean(string='Online Order Paid', default=False, help='is online order paid or not ?')
    online_order_status = fields.Selection([
        ('open', 'Open'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
        ('finalized', 'Finalized'),
        ('expired', 'Expired'),
    ], help='current status of online order in pos')
    order_priority = fields.Integer(
        string="Priority",
        compute="_compute_order_priority",
        store=True, help='order priority for online template'
    )
    is_online_order = fields.Boolean(string='Is Online Order', default=False,help='is online order or not ?')
    declined_time = fields.Datetime(string='Cancelled Date Time',help='time at which the order is declined from')
    channel_discount = fields.Float(string='Channel Discount',help='discount provided by the channel')
    channel_service_charge = fields.Float(string='Channel Service Charge',help='service charge for the channel')
    channel_delivery_charge = fields.Float(string='Channel Delivery Charge',help='delivery charge for the '
                                                                                 'channel')
    channel_tip_amount = fields.Float(string='Channel Tip',help='tips linked to the channel')
    channel_total_amount = fields.Float(string='Channel Total Amount',help='total order amount including channel '
                                                                           'charges')
    channel_tax = fields.Float(string='Channel Tax',help='channel specific tax amounts')
    bag_fee = fields.Float(string="Bag Fee",help='bag fee charged for the order')
    channel_order_reference = fields.Char(string='Channel Display Order ID',help='order reference provided by '
                                                                                 'deliverect')
    delivery_note = fields.Text(string='Delivery Note',help='delivery note for the order')
    pickup_time = fields.Datetime(string='Pickup Time',help='pick up time for the order')
    delivery_time = fields.Datetime(string='Delivery Time',help='delivery time for the order')
    channel_name = fields.Char(string='Channel',help='channel from which the order is received')
    customer_name = fields.Char(string='Customer Name',help='customer name for the order')
    customer_company_name = fields.Char(string='Customer Company Name',help='customer company name')
    customer_email = fields.Char(string='Customer Email',help='customer email')
    customer_note = fields.Char(string='Customer Note',help='customer note provided for the order')
    customer_phone = fields.Char(string='Customer Phone',help='customer phone number')

    @api.depends('online_order_status')
    def _compute_order_priority(self):
        """Compute order priority for showing online orders in the template based on online order status"""
        priority_mapping = {
            'open': 1,
            'approved': 2,
            'rejected': 3
        }
        for order in self:
            order.order_priority = priority_mapping.get(order.online_order_status, 4)

    @api.model
    def export_order_for_ui(self, order_id):
        """to get order data for printing receipt from online order screen"""
        order = self.env['pos.order'].browse(order_id)
        session = order.session_id
        order_ui = order._export_for_ui(order)
        order_ui['bag_fee']= order.bag_fee
        order_ui['channel_delivery_charge']= order.channel_delivery_charge
        order_ui['channel_discount']= order.channel_discount
        order_ui['channel_name']= order.channel_name
        order_ui['channel_order_reference']= order.channel_order_reference
        order_ui['channel_service_charge']= order.channel_service_charge
        order_ui['channel_tax']= order.channel_tax
        order_ui['channel_tip_amount']= order.channel_tip_amount
        order_ui['channel_total_amount']= order.channel_total_amount
        order_ui['customer_company_name']= order.customer_company_name
        order_ui['delivery_note']= order.delivery_note
        order_ui['delivery_time']= order.delivery_time
        order_ui['is_cooking']= order.is_cooking
        order_ui['order_payment_type']= order.order_payment_type
        order_ui['customer_name']= order.customer_name
        order_ui['customer_email']= order.customer_email
        order_ui['customer_note']= order.customer_note
        order_ui['customer_phone']= order.customer_phone
        order_ui['delivery_note']= order.delivery_note
        order_ui['state']= order.state
        order_ui['order_type']= order.order_type
        order_ui['partner_id']= [order.partner_id.id,order.partner_id.name]
        order_ui['pickup_time']= order.pickup_time
        order_ui['order_payment_type']= order.order_payment_type
        order_ui['note']= order.note

        order_ui['pos_session'] = {'id': session.id ,'name':session.name}
        order_ui['sequence_number'] = order.pos_reference
        order_ui['uid'] = order.id
        return [order_ui]

    def update_order_status_in_deliverect(self, status):
        """function to update the status of the order in deliverect"""
        url = f"https://api.deliverect.com/orderStatus/{self.online_order_id}"
        token = self.env['deliverect.api'].sudo().generate_auth_token()
        payload = {
            'orderId': self.online_order_id,
            'receiptId': self.pos_reference,
            'status': status,
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {token}"
        }
        response = requests.post(url, json=payload, headers=headers)
        _logger.info(f"Deliverect Order Status Update : {response.status_code} - {response.text}")

    def update_order_status(self, status):
        """function to update the status of the order"""
        if status == 'approved':
            self.write({'online_order_status': 'approved', 'is_cooking': True})
            self.lines.write({'is_cooking': True})
            self.update_order_status_in_deliverect(20)
            self.update_order_status_in_deliverect(50)
        elif status == 'finalized':
            self.write({'online_order_status': 'finalized'})
            self.update_order_status_in_deliverect(90)
        else:
            self.write({'online_order_status': 'rejected',
                        'declined_time': fields.Datetime.now(),
                        'order_status': 'cancel'})
            self.update_order_status_in_deliverect(110)
            deliverect_payment_method = self.env['pos.payment.method'].sudo().search([('company_id', '=',
                                                                                  self.company_id.id),
                                                                               ('is_deliverect_payment_method', '=',
                                                                                True)],limit=1)
            refund_action = self.refund()
            refund = self.env['pos.order'].sudo().browse(refund_action['res_id'])
            payment_context = {"active_ids": [refund.id], "active_id": refund.id}
            refund_payment = self.env['pos.make.payment'].sudo().with_context(**payment_context).create({
                'amount': refund.amount_total,
                'payment_method_id': deliverect_payment_method.id,
            })
            refund_payment.with_context(**payment_context).check()

    @api.model
    def get_new_orders(self, config_id):
        """function to return the count of open online orders"""
        session_id = self.env['pos.config'].browse(config_id).current_session_id.id
        return self.search_count([
            ('online_order_status', '=', 'open'),
            ('is_online_order', '=', True),
            ('amount_total', '>', 0),
            ('session_id', '=', session_id),
            ('config_id', '=', config_id)])

    @api.model
    def get_open_orders(self, config_id):
        """Return orders for the screen: include online and POS orders for current session.

        - Online orders: still filtered by decline window and status as before.
        - Offline POS orders: include draft/paid orders from current session.
        """
        session = self.env['pos.config'].browse(config_id).current_session_id
        session_id = session.id
        now = fields.Datetime.now()
        expiration_time = now - timedelta(minutes=1)

        fields_list = ['id', 'name', 'online_order_status', 'pos_reference', 'order_status', 'order_type',
                       'online_order_paid', 'state', 'amount_total', 'amount_tax', 'channel_order_reference',
                       'date_order', 'tracking_number', 'partner_id', 'user_id', 'lines', 'is_online_order',
                       'order_type_id', 'current_order_type', 'sh_order_type_id']

        # Online orders (recent or not declined long ago), any monetary amount > 0
        online_orders = self.search_read(
            ['|',
             ('declined_time', '=', False),
             ('declined_time', '>', expiration_time),
             ('is_online_order', '=', True),
             ('amount_total', '>', 0),
             ('config_id', '=', config_id),
             ('session_id', '=', session_id)],
            fields_list, order="order_priority, date_order DESC"
        )

        # Offline POS orders from current session (draft or paid)
        offline_orders = []
        if session_id:
            offline_orders = self.search_read(
                [
                    ('is_online_order', '=', False),
                    ('amount_total', '>', 0),
                    ('config_id', '=', config_id),
                    ('session_id', '=', session_id),
                    ('state', 'in', ['draft', 'paid'])
                ],
                fields_list, order="date_order DESC"
            )
            # Normalize for UI: treat offline orders as 'approved' for display logic, but do not add online actions
            for o in offline_orders:
                o['online_order_status'] = o.get('online_order_status') or 'approved'

        orders = online_orders + offline_orders
        for order in orders:
            order['amount_total'] = "{:.2f}".format(order['amount_total'])
            order['amount_tax'] = "{:.2f}".format(order['amount_tax'])
        all_line_ids = [line_id for order in orders for line_id in order['lines']]
        lines = self.env['pos.order.line'].search_read(
            [('id', 'in', all_line_ids)],
            ['id', 'full_product_name', 'product_id', 'qty', 'price_unit', 'price_subtotal', 'price_subtotal_incl']
        )
        for line in lines:
            line['price_unit'] = "{:.2f}".format(line['price_unit'])
            line['price_subtotal'] = "{:.2f}".format(line['price_subtotal'])
            line['price_subtotal_incl'] = "{:.2f}".format(line['price_subtotal_incl'])
        line_mapping = {line['id']: line for line in lines}
        for order in orders:
            order['lines'] = [line_mapping[line_id] for line_id in order['lines'] if line_id in line_mapping]
        return orders

    @api.model
    def export_for_ui_table_draft(self, table_ids):
        """override method to include online orders"""
        offline_orders = self.env['pos.order'].search([
            ('state', '=', 'draft'),
            ('table_id', 'in', table_ids),
        ])
        online_orders = self.env['pos.order'].search([
            ('is_online_order', '=', True),
            ('state', '=', 'draft'),
            ('online_order_status', 'in', ['approved', 'finalized'])])
        orders = offline_orders | online_orders
        return orders.export_for_ui()

    @api.model
    def get_orders(self, config_id, filters=None, page=1, page_size=50):
        """Return combined orders (online + POS) with filters and pagination.

        :param int config_id: current POS config
        :param dict filters: optional filters: {
            'date_preset': 'today'|'yesterday'|'7d'|'month'|None,
            'date_from': iso str,
            'date_to': iso str,
            'status': 'all'|'open'|'paid'|'refunded'|'cancelled',
            'source': 'all'|'online'|'pos',
            'query': str
        }
        :param int page: 1-based page index
        :param int page_size: page size
        :return: dict with 'orders' list and 'has_more' boolean
        """
        filters = filters or {}
        domain = [('config_id', '=', config_id)]

        # Source filter
        source = filters.get('source', 'all')
        if source == 'online':
            domain.append(('is_online_order', '=', True))
        elif source == 'pos':
            domain.append(('is_online_order', '=', False))

        # Date preset or explicit range
        date_from = filters.get('date_from')
        date_to = filters.get('date_to')
        preset = filters.get('date_preset')
        if not (date_from and date_to) and preset:
            now = fields.Datetime.now()
            if preset == 'today':
                # start of day to end of day
                date_from = fields.Datetime.to_string(fields.Datetime.context_timestamp(self, now).replace(hour=0, minute=0, second=0, microsecond=0))
                date_to = fields.Datetime.to_string(fields.Datetime.context_timestamp(self, now).replace(hour=23, minute=59, second=59, microsecond=999999))
            elif preset == 'yesterday':
                y = now - timedelta(days=1)
                date_from = fields.Datetime.to_string(fields.Datetime.context_timestamp(self, y).replace(hour=0, minute=0, second=0, microsecond=0))
                date_to = fields.Datetime.to_string(fields.Datetime.context_timestamp(self, y).replace(hour=23, minute=59, second=59, microsecond=999999))
            elif preset == '7d':
                d = now - timedelta(days=6)
                date_from = fields.Datetime.to_string(fields.Datetime.context_timestamp(self, d).replace(hour=0, minute=0, second=0, microsecond=0))
                date_to = fields.Datetime.to_string(fields.Datetime.context_timestamp(self, now).replace(hour=23, minute=59, second=59, microsecond=999999))
            elif preset == 'month':
                first = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                date_from = fields.Datetime.to_string(fields.Datetime.context_timestamp(self, first))
                date_to = fields.Datetime.to_string(fields.Datetime.context_timestamp(self, now).replace(hour=23, minute=59, second=59, microsecond=999999))
        if date_from:
            domain.append(('date_order', '>=', date_from))
        if date_to:
            domain.append(('date_order', '<=', date_to))

        # Status filter
        status = filters.get('status', 'all')
        status_domain = []
        if status and status != 'all':
            if status == 'open':
                status_domain = [('state', '=', 'draft')]
            elif status == 'paid':
                status_domain = [('state', '=', 'paid')]
            elif status == 'refunded':
                status_domain = [('amount_total', '<', 0)]
            elif status == 'cancelled':
                status_domain = ['|', ('order_status', '=', 'cancel'), ('state', '=', 'cancel')]
        # Query filter
        query = filters.get('query')
        if query:
            qd = ['|', '|',
                  ('pos_reference', 'ilike', query),
                  ('channel_order_reference', 'ilike', query),
                  ('partner_id.name', 'ilike', query)]
            domain = ['&'] + domain + [qd]

        complete_domain = domain
        if status_domain:
            complete_domain = ['&'] + domain + [status_domain]

        # Build fields list dynamically to avoid crashes if optional modules are absent
        candidate_fields = [
            'id', 'name', 'pos_reference', 'state', 'amount_total', 'amount_tax', 'date_order',
            'partner_id', 'user_id', 'lines',
            # Optional/custom fields below; included only if present
            'online_order_status', 'order_status', 'order_type', 'online_order_paid', 'channel_order_reference',
            'tracking_number', 'is_online_order', 'is_cooking', 'sh_order_type_id', 'order_type_id', 'current_order_type',
            'channel_name',
        ]
        fields_list = [f for f in candidate_fields if f in self._fields]

        offset = max(0, (page - 1) * page_size)
        orders = self.search_read(complete_domain, fields_list, offset=offset, limit=page_size, order="date_order DESC")

        # Enrich with display fields without breaking if external modules absent
        for o in orders:
            # Channel/receipt display: if online, use channel ref; else show POS receipt/name
            channel_disp = o.get('channel_order_reference') or ''
            if not o.get('is_online_order'):
                channel_disp = o.get('pos_reference') or o.get('tracking_number') or o.get('name') or ''
            o['channel_display'] = channel_disp or ' - '
            # Channel icon mapping (known channels -> slug)
            partner_name = ''
            if o.get('partner_id') and isinstance(o.get('partner_id'), (list, tuple)) and len(o.get('partner_id')) > 1:
                partner_name = (o['partner_id'][1] or '').strip()
            name = (o.get('channel_name') or partner_name or '').strip()
            slug = None
            if name:
                lookup = {
                    'uber eats': 'uber_eats',
                    'doordash': 'doordash',
                    'flipdish': 'flipdish',
                    'hungrypanda': 'hungrypanda',
                    'fantuan': 'fantuan',
                    'skipthedishes': 'skip_the_dishes',
                    'ritual': 'ritual',
                    'ordering': 'ordering',
                    'foodhub': 'foodhub',
                    'dood': 'dood',
                    'popmenu': 'popmenu',
                    'horago': 'horago',
                    'horego': 'horago',
                    'relayy digital services': 'relayy',
                    'b bot': 'bbot',
                    'bbot': 'bbot',
                    'arch2order': 'arch2order',
                    'plento': 'plento',
                    'tablevibe': 'tablevibe',
                    'jetsontech': 'jetson',
                    'qikserve': 'qikserve',
                    'deliverect': 'deliverect',
                    'deliverect kds': 'deliverect',
                }
                key = re.sub(r"\s+", " ", name).strip().lower()
                slug = lookup.get(key)
                if not slug:
                    # generic slugify
                    slug = re.sub(r"[^a-z0-9]+", "_", key).strip('_')
            o['channel_slug'] = slug or ''
            if slug:
                filename = f"{slug}.svg"
                res_path = get_resource_path('apptology_deliverect', 'static', 'src', 'img', 'channels', filename)
                if res_path and os.path.exists(res_path):
                    o['channel_icon'] = f"/apptology_deliverect/static/src/img/channels/{filename}"
                else:
                    o['channel_icon'] = ''
            # Order type display from SH order type if present, else fallback to deliverect mapping or '-'
            ot_name = None
            if o.get('sh_order_type_id'):
                ot_name = (o['sh_order_type_id'][1] if isinstance(o['sh_order_type_id'], (list, tuple)) and len(o['sh_order_type_id']) > 1 else None)
            elif o.get('order_type_id'):
                # Many2one return [id, name]
                ot_name = (o['order_type_id'][1] if isinstance(o['order_type_id'], (list, tuple)) and len(o['order_type_id']) > 1 else None)
            elif o.get('current_order_type'):
                ot_name = (o['current_order_type'][1] if isinstance(o['current_order_type'], (list, tuple)) and len(o['current_order_type']) > 1 else None)
            if not ot_name:
                code = o.get('order_type')
                mapping = {'1': 'Pick Up', '2': 'Delivery', '3': 'Eat In'}
                ot_name = mapping.get(code) if code else None
            o['order_type_display'] = ot_name or ' - '

            # Kitchen status display logic
            ks = ''
            order_status = o.get('order_status')
            online_status = o.get('online_order_status')
            is_online = bool(o.get('is_online_order'))
            is_cooking = bool(o.get('is_cooking')) if 'is_cooking' in o else False

            if order_status == 'cancel':
                ks = 'Cancelled'
            elif order_status == 'ready':
                ks = 'Ready'
            else:
                if is_online:
                    if online_status not in ('approved', 'finalized'):
                        ks = 'Draft'
                    else:
                        ks = 'In Progress' if is_cooking else 'Right Away'
                else:
                    # In-store orders: infer from cooking flag or order_status
                    ks = 'In Progress' if (is_cooking or order_status == 'draft') else 'Right Away'
            o['kitchen_status_display'] = ks

        for order in orders:
            # normalize display values
            order['amount_total'] = "{:.2f}".format(order['amount_total'])
            order['amount_tax'] = "{:.2f}".format(order['amount_tax'])

        # Lines foldout
        all_line_ids = [line_id for order in orders for line_id in order['lines']]
        lines = self.env['pos.order.line'].search_read(
            [('id', 'in', all_line_ids)],
            ['id', 'full_product_name', 'product_id', 'qty', 'price_unit', 'price_subtotal', 'price_subtotal_incl']
        )
        for line in lines:
            line['price_unit'] = "{:.2f}".format(line['price_unit'])
            line['price_subtotal'] = "{:.2f}".format(line['price_subtotal'])
            line['price_subtotal_incl'] = "{:.2f}".format(line['price_subtotal_incl'])
        line_mapping = {line['id']: line for line in lines}
        for order in orders:
            order['lines'] = [line_mapping.get(line_id) for line_id in order['lines'] if line_id in line_mapping]

        has_more = len(orders) == page_size
        return {
            'orders': orders,
            'has_more': has_more,
        }

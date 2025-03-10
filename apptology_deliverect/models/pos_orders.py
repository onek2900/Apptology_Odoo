# -*- coding: utf-8 -*-
import logging
import requests
from datetime import timedelta

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    """Inheriting the pos order model to add new fields"""
    _inherit = "pos.order"

    order_type = fields.Selection([
        ('1', 'Pick up'),
        ('2', 'Delivery')
    ], string='Order Type', default='1')
    online_order_id = fields.Char(string='Online Order ID')
    online_order_paid = fields.Boolean(string='Online Order Paid', default=False)
    online_order_status = fields.Selection([
        ('open', 'Open'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
        ('finalized', 'Finalized'),
        ('expired', 'Expired'),
    ])
    order_priority = fields.Integer(
        string="Priority",
        compute="_compute_order_priority",
        store=True
    )
    is_online_order = fields.Boolean(string='Is Online Order', default=False)
    declined_time = fields.Datetime(string='Cancelled Date Time')

    @api.depends('online_order_status')
    def _compute_order_priority(self):
        """function to compute the priority of the order based on the status of the online order"""
        for order in self:
            if order.online_order_status == 'open':
                order.order_priority = 1
            elif order.online_order_status == 'approved':
                order.order_priority = 2
            elif order.online_order_status == 'rejected':
                order.order_priority = 3
            else:
                order.order_priority = 4

    def update_order_status_in_deliverect(self, status):
        """function to update the status of the order in deliverect"""
        url = f"https://api.staging.deliverect.com/orderStatus/{self.online_order_id}"
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
        else:
            self.write({'online_order_status': 'rejected',
                        'declined_time': fields.Datetime.now(),
                        'order_status': 'cancel'})
            self.update_order_status_in_deliverect(110)
            deliverect_payment_method = self.env.ref("apptology_deliverect.pos_payment_method_deliverect")
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
        """function to get the new orders from deliverect"""
        session_id = self.env['pos.config'].browse(config_id).current_session_id.id
        return self.search_count([
            ('online_order_status', '=', 'open'),
            ('is_online_order', '=', True),
            ('amount_total', '>', 0),
            ('session_id', '=', session_id),
            ('config_id', '=', config_id)])

    @api.model
    def get_open_orders(self, config_id):
        """function to get the open orders from deliverect"""
        session_id = self.env['pos.config'].browse(config_id).current_session_id.id
        now = fields.Datetime.now()
        expiration_time = now - timedelta(minutes=1)
        orders = self.search_read(
            ['|',
             ('declined_time', '=', False),
             ('declined_time', '>', expiration_time),
             ('is_online_order', '=', True),
             ('amount_total', '>', 0),
             ('config_id', '=', config_id),
             ('session_id', '=', session_id)
             ],
            ['id', 'online_order_status', 'pos_reference', 'order_status', 'order_type', 'online_order_paid', 'state',
             'amount_total', 'amount_tax',
             'date_order',
             'partner_id',
             'user_id', 'lines'], order="order_priority, date_order DESC"
        )
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

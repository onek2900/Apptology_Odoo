# -*- coding: utf-8 -*-
from datetime import timedelta
from email.policy import default
import requests
import logging

from odoo import api, fields, models
_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    """Inheriting the pos order model"""
    _inherit = "pos.order"

    order_type = fields.Selection([
        ('1', 'Pick up'),
        ('2', 'Delivery'),
        ('3', 'Eat In'),
        ('4', 'Curbside')
    ], string='Order Type', default='1')
    online_order_id = fields.Char(string='Online Order ID')
    online_order_status = fields.Selection([
        ('open', 'Open'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
        ('delivered', 'Delivered'),
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
        for order in self:
            if order.online_order_status == 'open':
                order.order_priority = 1
            elif order.online_order_status == 'approved':
                order.order_priority = 2
            elif order.online_order_status == 'rejected':
                order.order_priority = 3
            else:
                order.order_priority = 4

    def update_order_status_in_deliverect(self,status):
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

        if status == 'approved':
            self.write({'online_order_status': 'approved','is_cooking':True})
            self.update_order_status_in_deliverect(20)
            self.update_order_status_in_deliverect(50)
        else:
            self.write({'online_order_status': 'rejected',
                        'declined_time': fields.Datetime.now(),
                        'order_status':'cancel'})
            self.update_order_status_in_deliverect(110)


    @api.model
    def get_new_orders(self,config_id):
        return self.search_count([
            ('online_order_status', '=', 'open'),
            ('is_online_order', '=', True),
            ('amount_total','>',0),
            ('config_id','=',config_id)])


    @api.model
    def get_open_orders(self,config_id):
        print('config : ',config_id)
        now=fields.Datetime.now()
        expiration_time=now-timedelta(minutes=1)
        orders = self.search_read(
            ['|',
                ('declined_time', '=', False),
                ('declined_time', '>', expiration_time),
                ('is_online_order', '=', True),
                ('amount_total','>',0),
                ('config_id', '=', config_id)
            ],
            ['id', 'online_order_status', 'pos_reference','order_status', 'amount_total', 'amount_tax', 'date_order', 'partner_id',
             'user_id', 'lines'],order="order_priority, date_order DESC"
        )
        all_line_ids = [line_id for order in orders for line_id in order['lines']]
        lines = self.env['pos.order.line'].search_read(
            [('id', 'in', all_line_ids)],
            ['id', 'full_product_name', 'product_id', 'qty', 'price_unit', 'price_subtotal', 'price_subtotal_incl']
        )
        line_mapping = {line['id']: line for line in lines}
        for order in orders:
            order['lines'] = [line_mapping[line_id] for line_id in order['lines'] if line_id in line_mapping]
        return orders

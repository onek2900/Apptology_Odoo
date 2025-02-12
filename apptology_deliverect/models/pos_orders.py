# -*- coding: utf-8 -*-
from email.policy import default

from odoo import api, fields, models



class PosOrder(models.Model):
    """Inheriting the pos order model"""
    _inherit = "pos.order"

    order_type = fields.Selection([
        ('1', 'Pick up'),
        ('2', 'Delivery'),
        ('3', 'Eat In'),
        ('4', 'Curbside')
    ], string='Order Type', default='1')
    order_approved=fields.Boolean(string='Order Approved',default=False)
    is_deliverect_order=fields.Boolean(string='Deliverect Order',default=False)

    def update_order_status(self,status):
        print('inside change order state',self)
        if status=='approved':
            self.write({'state':'paid','order_approved':True})
        else:
            self.write({'state':'cancel'})
        print(self.order_approved,self.state)
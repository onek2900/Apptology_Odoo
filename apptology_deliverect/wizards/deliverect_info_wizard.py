# -*- coding: utf-8 -*-
from odoo import models, fields


class DeliverectInfoWizard(models.TransientModel):
    """Class for Deliverect Information Wizard"""
    _name = 'deliverect.info.wizard'
    _description = 'Deliverect Information Wizard'

    registration_url = fields.Char(string='Registration URL', readonly=True,help='registration url to be used in '
                                                                                 'deliverect')
    orders_url = fields.Char(string='Orders URL', readonly=True,help='order url to be used in deliverect')
    products_url = fields.Char(string='Products URL', readonly=True,help='product sync url to be used in deliverect')
    location_id = fields.Char(string='Location ID', readonly=True,help='pos specific location id provided by '
                                                                       'deliverect')
    status_message = fields.Char(string='Status', readonly=True)
    internal_pos_id = fields.Char(string='POS Id', readonly=True,help='pos id provided to deliverect')
    order_status_message = fields.Char(string='Order Status', readonly=True)

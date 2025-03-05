# -*- coding: utf-8 -*-
from odoo import models, fields


class DeliverectInfoWizard(models.TransientModel):
    """Class for Deliverect Information Wizard"""
    _name = 'deliverect.info.wizard'
    _description = 'Deliverect Information Wizard'

    registration_url = fields.Char(string='Registration URL', readonly=True)
    orders_url = fields.Char(string='Orders URL', readonly=True)
    products_url = fields.Char(string='Products URL', readonly=True)
    location_id = fields.Char(string='Location ID', readonly=True)
    status_message = fields.Char(string='Status', readonly=True)
    order_status_message = fields.Char(string='Order Status', readonly=True)

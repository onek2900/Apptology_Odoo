# -*- coding: utf-8 -*-
from odoo import models, fields


class DeliverectInfoWizard(models.TransientModel):
    """Class for Deliverect Information Wizard"""
    _name = 'deliverect.info.wizard'
    _description = 'Deliverect Information Wizard'

    pos_config_id = fields.Many2one('pos.config', string="Point of Sale")
    registration_url = fields.Char(string='Registration URL', readonly=True)
    orders_url = fields.Char(string='Orders URL', readonly=True)
    products_url = fields.Char(string='Products URL', readonly=True)
    location_id = fields.Char(string='Location ID', readonly=True)
    status_message = fields.Char(string='Status', readonly=True)
    internal_pos_id = fields.Char(string='POS Id', readonly=True)
    order_status_message = fields.Char(string='Order Status', readonly=True)

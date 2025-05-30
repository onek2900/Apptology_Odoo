# -*- coding: utf-8 -*-

import base64
import secrets

from odoo import api, fields, models


class KitchenScreen(models.Model):
    """Kitchen Screen model for the cook"""
    _name = 'kitchen.screen'
    _description = 'Pos Kitchen Screen'
    _rec_name = 'sequence'

    def _pos_shop_id(self):
        """Domain for the Pos Shop"""
        kitchen = self.search([])
        if kitchen:
            return [(
                    'id', 'not in', [rec.id for rec in kitchen.pos_config_id])]
        else:
            return []
    sequence = fields.Char(readonly=True, default='New',
                           copy=False, tracking=True, help="Sequence of items")
    pos_config_id = fields.Many2one('pos.config', string='Allowed POS',
                                    domain=_pos_shop_id,
                                    help="Allowed POS for kitchen")
    pos_categ_ids = fields.Many2many('pos.category',
                                     string='Allowed POS Category',
                                     help="Allowed POS Category"
                                          "for the corresponding Pos")
    shop_number = fields.Integer(related='pos_config_id.id', string='Customer',
                                 help="Id of the POS")

    def render_kitchen_screen(self):
        """Redirect to corresponding kitchen screen for the cook"""
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': '/apptology_kitchen_screen?shop_id=%s' % self.pos_config_id.id,
        }

    def render_order_screen(self):
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': '/apptology_order_screen?screen_id=%s' % self.id,
        }

    @api.model
    def create(self, vals):
        """Used to create sequence"""
        if vals.get('sequence', 'New') == 'New':
            vals['sequence'] = self.env['ir.sequence'].next_by_code(
                'kitchen.screen')
        result = super(KitchenScreen, self).create(vals)
        return result

# Copyright (C) Softhealer Technologies.
# Part of Softhealer Technologies.

from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit = 'res.partner'

    sh_own_customer = fields.Many2many(
        'res.users', 'pos_own_partner_list', string='Allocate Sale Person')

    @api.model
    def create_from_ui(self, partner):
        res = super(ResUsers, self).create_from_ui(partner)
        add = self.env['res.partner'].browse(res)
        add.write({'sh_own_customer': [(6, 0, [self.env.user.id])]})
        return res

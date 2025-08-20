# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from pkg_resources import require
from odoo import models, fields, api, _

class ShToppingGroup(models.Model):
    _name = 'sh.topping.group'
    _description = "Define Toppings products"

    name = fields.Char(string="Name", required=True)
    toppinds_ids = fields.Many2many('product.product', string="Toppings", domain="[('available_in_pos', '=', True)]")

class MassUpdateToppings(models.TransientModel):
    _name = 'sh.mass.update.topings'
    _description= 'mass update topping'

    sh_topping_group_ids = fields.Many2many('sh.topping.group', 'massupdate_topping_group', string="Toppings Groups")
    sh_topping_product_ids = fields.Many2many('product.product', string="Toppings", domain="[('available_in_pos', '=', True)]")

    @api.onchange('sh_topping_group_ids')
    def _onchange_sh_topping_group_ids(self):
            topping_groups = self.env['sh.topping.group'].browse(self.sh_topping_group_ids.ids)
            topping_ids = []
            if topping_groups:
                for topping_groupid in topping_groups: 
                    for tid in topping_groupid.toppinds_ids:
                        topping_ids.append(tid.id)
            self.update({'sh_topping_product_ids':[(6,0,topping_ids)] })

    def updateToppings(self):
        #update selected product toppings
        products = self.env['product.product'].browse(self._context.get('active_ids'))
        for product in products:
            product.sh_topping_group_ids = self.sh_topping_group_ids
            product.sh_topping_ids = self.sh_topping_product_ids

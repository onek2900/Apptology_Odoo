# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models, fields, api

class Partner(models.Model):
    _inherit = 'res.partner'

    @api.model_create_multi
    def create(self, vals):
        res = super().create(vals)
        if res.id:
            self.env['customer.update'].broadcast_partner(res)
        return res

    def write(self, vals):
        if 'active' in vals and vals.get('active')==False:
            for rec in self:
                self.env['customer.update'].sudo().create({'delete_ids':str(rec.id)})

        for rec in self:
            delete_ids = self.env['customer.update'].sudo().search([('delete_ids','=',str(rec.id))])
            if delete_ids:
                delete_ids.sudo().unlink()
            self.env['customer.update'].broadcast_partner(rec)
    
        res = super(Partner, self).write(vals)
      
        return res
    
    def unlink(self):
        for rec in self:
            last_id = self.env['customer.update'].sudo().search([])
            self.env['customer.update'].sudo().create({'delete_ids':str(rec.id)})
        res = super(Partner, self).unlink()       
        return res
    #

    
    
class PartnerUpdate(models.Model):
    _name = 'customer.update'
    _description = "send notifucation to pos"

    delete_ids = fields.Char("Delete Ids")
                    
    def broadcast_partner(self, partner):
        if partner.id:
            data = partner.read(['name','street','city','state_id','country_id','vat','lang',
                 'phone','zip','mobile','email','barcode','write_date',
                 'property_account_position_id','property_product_pricelist'])
            if data and len(data) > 0:
                pos_session = self.env['pos.session'].search(
                    [('state', 'in', ['opened', 'opening_control'])])
                if pos_session:
                    for each_session in pos_session:
                        self.env['bus.bus']._sendmany(
                            [[each_session.user_id.partner_id, 'customer_update', data]])
                  
    
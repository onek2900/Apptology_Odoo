# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models, fields, api
    
class ProductTemplate(models.Model):
    _inherit = 'product.template'
  
    def write(self, vals):
    
        if 'active' in vals and vals.get('active')==False:
            for rec in self:
                if rec.product_variant_count == 1 and rec.product_variant_ids and rec.product_variant_ids[0]:
                    self.env['product.update'].sudo().create({'delete_ids':str(rec.product_variant_ids[0].id)})
    
        res = super(ProductTemplate, self).write(vals)
    
        if not 'available_in_pos' in vals and not 'active' in vals:
            for rec in self:
                if rec.product_variant_count == 1 and rec.product_variant_ids and rec.product_variant_ids[0]:
                    self.env['product.update'].broadcast_product(rec.product_variant_ids[0])
        return res
    
    def unlink(self):
        for rec in self:
            if rec.product_variant_count == 1 and rec.product_variant_ids and rec.product_variant_ids[0]:
                
                self.env['product.update'].sudo().create({'delete_ids':str(rec.product_variant_ids[0].id)})
        res = super(ProductTemplate, self).unlink()       
        return res
    
class Product(models.Model):
    _inherit = 'product.product'

    @api.model_create_multi
    def create(self, vals):
        res = super().create(vals)
        for rec in res:
            if rec.id:
                self.env['product.update'].broadcast_product(rec)
        return res

    def write(self, vals):
        if 'active' in vals and vals.get('active')==False:
            for rec in self:
                self.env['product.update'].sudo().create({'delete_ids':str(rec.id)})
                self.env['product.update'].broadcast_product(rec)
    
        if 'active' in vals and vals.get('active')==True:
            for rec in self:
                delete_ids = self.env['product.update'].sudo().search([('delete_ids','=',str(rec.id))])
                if delete_ids:
                    delete_ids.sudo().unlink()
                self.env['product.update'].broadcast_product(rec)
    
        res = super(Product, self).write(vals)
        if not 'available_in_pos' in vals  and not 'active' in vals:
            for rec in self:
                self.env['product.update'].broadcast_product(rec)
        return res
    
    def unlink(self):
        for rec in self:
            last_id = self.env['product.update'].sudo().search([])
            self.env['product.update'].sudo().create({'delete_ids':str(rec.id)})
        res = super(Product, self).unlink()       
        return res
    #

    
    
class PosStockChannel(models.Model):
    _name = 'product.update'
    _description = "send notifucation to pos"

    delete_ids = fields.Char("Delete Ids")

    def _get_pos_ui_product_category(self, params):
        categories = self.env['product.category'].search_read(**params['search_params'])
        category_by_id = {category['id']: category for category in categories}
        for category in categories:
            category['parent'] = category_by_id[category['parent_id'][0]] if category['parent_id'] else None
        return categories
    
    def _loader_params_product_category(self):
        return {'search_params': {'domain': [], 'fields': ['name', 'parent_id']}}
                    
    def broadcast_product(self, product):
        
        if product.id:
            fields = ['display_name', 'image_128', 'lst_price', 'standard_price', 'categ_id', 'pos_categ_ids', 'taxes_id','barcode', 'default_code', 'to_weight', 'uom_id', 'description_sale', 'description', 'product_tmpl_id','tracking', 'write_date', 'available_in_pos', 'attribute_line_ids', 'active','combo_ids', 'suggestion_line', 'barcode_line_ids', 'sh_order_label_demo_product', "sh_product_non_returnable", "sh_product_non_exchangeable", 'sh_select_user', 'sh_topping_ids','sh_is_global_topping','sh_topping_group_ids', 'sh_alternative_products', 'name', 'product_template_attribute_value_ids', 'product_variant_count', 'sh_secondary_uom', 'sh_is_secondary_unit', "type", "qty_available", "virtual_available", "weight", "volume", ]
            if 'optional_product_ids' in self.env['product.product']._fields:
                fields.append('optional_product_ids')
            data = product.read(fields)
            if data and len(data) > 0:
                pos_session = self.env['pos.session'].search(
                    [('state', 'in', ['opened', 'opening_control'])])
                categories = self._get_pos_ui_product_category(self._loader_params_product_category())
                product_category_by_id = {category['id']: category for category in categories}
                if pos_session:

                    for each_data in data:
                        each_data['categ'] = product_category_by_id[each_data['categ_id'][0]]
                    for each_session in pos_session:
                        self.env['bus.bus']._sendmany(
                            [[each_session.user_id.partner_id, 'product_update', data]])
                else:
                    for each_data in data:
                        each_data['categ'] = product_category_by_id[product.categ_id.id]
                    self.env['bus.bus']._sendmany([[self.env.user.partner_id, 'product_update', data]])
                    
    
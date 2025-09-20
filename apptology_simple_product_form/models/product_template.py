from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # Ensure new products are available in POS by default
    available_in_pos = fields.Boolean(default=True)

    # Real template-level many2many so it works before the first save
    sh_topping_group_ids = fields.Many2many(
        comodel_name='sh.topping.group',
        relation='product_template_sh_topping_group_rel',
        column1='product_tmpl_id',
        column2='topping_group_id',
        string='Topping Groups',
        help='Groups used to auto-populate toppings for this product.'
    )
    sh_topping_ids = fields.Many2many(
        comodel_name='product.product',
        relation='product_template_sh_topping_rel',
        column1='product_tmpl_id',
        column2='topping_product_id',
        string='Toppings',
        domain="[('available_in_pos', '=', True)]",
        help='Toppings available for this product.'
    )

    @api.onchange('sh_topping_group_ids')
    def _onchange_sh_topping_group_ids(self):
        # Auto-fill toppings from selected groups to mirror product.product behavior
        for template in self:
            topping_ids = []
            for grp in template.sh_topping_group_ids:
                topping_ids.extend(grp.toppinds_ids.ids)
            template.sh_topping_ids = [(6, 0, list(set(topping_ids)))]

    def _sync_toppings_to_variants(self):
        for template in self:
            group_ids = template.sh_topping_group_ids.ids
            topping_ids = template.sh_topping_ids.ids
            if template.product_variant_ids:
                template.product_variant_ids.write({
                    'sh_topping_group_ids': [(6, 0, group_ids)],
                    'sh_topping_ids': [(6, 0, topping_ids)],
                })

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        # After variants are created, propagate the toppings/groups
        records._sync_toppings_to_variants()
        return records

    def write(self, vals):
        res = super().write(vals)
        if 'sh_topping_group_ids' in vals or 'sh_topping_ids' in vals:
            self._sync_toppings_to_variants()
        return res

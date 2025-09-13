from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # Ensure new products are available in POS by default
    available_in_pos = fields.Boolean(default=True)

    # Related fields to expose product.product toppings on the template form
    # New canonical names aligned with sh_pos_all_in_one_retail
    sh_topping_group_ids = fields.Many2many(
        comodel_name='sh.topping.group',
        string='Topping Groups',
        related='product_variant_id.sh_topping_group_ids',
        readonly=False,
    )
    sh_topping_ids = fields.Many2many(
        comodel_name='product.product',
        string='Toppings',
        related='product_variant_id.sh_topping_ids',
        readonly=False,
        domain="[('available_in_pos', '=', True)]",
    )

    @api.onchange('sh_topping_group_ids')
    def _onchange_sh_topping_group_ids(self):
        # Auto-fill toppings from selected groups to mirror product.product behavior
        for template in self:
            topping_ids = []
            for grp in template.sh_topping_group_ids:
                topping_ids.extend(grp.toppinds_ids.ids)
            template.sh_topping_ids = [(6, 0, list(set(topping_ids)))]

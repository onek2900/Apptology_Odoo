# Copyright (C) Softhealer Technologies.

from odoo import models, fields, api


class POSProductTemplateLine(models.Model):
    _name = "pos.product.template.line"
    _description = "pos products template lines"

    name = fields.Many2one(
        "product.product",
        string="Product ",
        required=True,
        domain=[("available_in_pos", "=", True)],
    )
    description = fields.Char("Description ")
    ordered_qty = fields.Float("Ordered Qty ")
    unit_price = fields.Float("Unit Price ")
    discount = fields.Float("Discount(%) ")
    product_uom = fields.Many2one("uom.uom", string="Uom ")
    price_subtotal = fields.Float(
        compute="_compute_amount", string="Subtotal ", readonly=True, store=True
    )
    pos_template_id = fields.Many2one("pos.product.template", string="POS Template Id ")

    @api.depends("ordered_qty", "unit_price")
    def _compute_amount(self):
        """
        Compute the amounts of the template line.
        """
        if self:
            for line in self:
                subtoal = line.unit_price * line.ordered_qty
                line.update(
                    {
                        "price_subtotal": subtoal,
                    }
                )

    @api.onchange("name")
    def product_change(self):
        if self.name:
            product_obj = self.env["product.product"].search(
                [("id", "=", self.name.id)]
            )

            if product_obj:
                self.description = product_obj.display_name
                self.ordered_qty = 1
                self.unit_price = product_obj.list_price
                self.discount = 0
                self.product_uom = product_obj.uom_id.id


class POSProductTemplate(models.Model):
    _name = "pos.product.template"
    _description = "pos product template "

    name = fields.Char("Template ", required=True)
    pos_product_template_ids = fields.One2many(
        "pos.product.template.line", "pos_template_id", string="POS Product Line "
    )
    active = fields.Boolean("Active ", default=True)
    discount_total = fields.Float(compute="_get_discount", string="Discount ")
    amount_total = fields.Float(compute="_amount_all", string="Total ")
    final_total = fields.Float(compute="_get_final_total", string="Final Total ")

    @api.depends("pos_product_template_ids.price_subtotal")
    def _amount_all(self):
        """
        Compute the total amounts of the template line.
        """
        for rec in self:
            amount_total = 0.0
            for line in rec.pos_product_template_ids:
                amount_total += line.price_subtotal
            rec.update(
                {
                    "amount_total": amount_total,
                }
            )

    @api.depends(
        "pos_product_template_ids.discount", "pos_product_template_ids.price_subtotal"
    )
    def _get_discount(self):
        for rec in self:
            discount = 0.0
            for line in rec.pos_product_template_ids:
                discount += (line.discount * line.price_subtotal) / 100
            rec.update(
                {
                    "discount_total": discount,
                }
            )

    @api.depends("amount_total", "discount_total")
    def _get_final_total(self):
        for template in self:
            template.final_total = template.amount_total - template.discount_total

# Copyright (C) Softhealer Technologies.
# Part of Softhealer Technologies.

from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero


class PosConfig(models.Model):
    _inherit = 'pos.config'

    sh_display_stock = fields.Boolean("Display Warehouse Stock")
    sh_display_by = fields.Selection([('location', 'Location'), (
        'warehouse', 'Warehouse')], string="Display Qty By", default="warehouse")
    sh_min_qty = fields.Integer("Min Quantity")
    sh_show_qty_location = fields.Boolean("Only show quantity in POS location")
    sh_pos_location = fields.Many2one('stock.location', "POS Location", domain=[("usage", "in", ["internal"])])


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def _create_picking_from_pos_order_lines(self, location_dest_id, lines, picking_type, partner=False):
        """We'll create some picking based on order_lines"""

        pickings = self.env['stock.picking']
        stockable_lines = lines.filtered(lambda l: l.product_id.type in [
                                         'product', 'consu'] and not float_is_zero(l.qty, precision_rounding=l.product_id.uom_id.rounding))
        if not stockable_lines:
            return pickings
        positive_lines = stockable_lines.filtered(lambda l: l.qty > 0)
        negative_lines = stockable_lines - positive_lines
        if positive_lines:
            if lines[0] and lines[0].order_id and lines[0].order_id.config_id and lines[0].order_id.config_id.sh_pos_location and lines[0].order_id.config_id.sh_pos_location.id:
                location_id = lines[0].order_id.config_id.sh_pos_location.id
            else:
                location_id = picking_type.default_location_src_id.id
            positive_picking = self.env['stock.picking'].create(
                self._prepare_picking_vals(
                    partner, picking_type, location_id, location_dest_id)
            )

            positive_picking._create_move_from_pos_order_lines(positive_lines)
            try:
                with self.env.cr.savepoint():
                    positive_picking._action_done()
            except (UserError, ValidationError):
                pass

            pickings |= positive_picking
        if negative_lines:
            if picking_type.return_picking_type_id:
                return_picking_type = picking_type.return_picking_type_id
                return_location_id = return_picking_type.default_location_dest_id.id
            else:
                return_picking_type = picking_type
                return_location_id = picking_type.default_location_src_id.id

            negative_picking = self.env['stock.picking'].create(
                self._prepare_picking_vals(
                    partner, return_picking_type, location_dest_id, return_location_id)
            )
            negative_picking._create_move_from_pos_order_lines(negative_lines)
            try:
                with self.env.cr.savepoint():
                    negative_picking._action_done()
            except (UserError, ValidationError):
                pass
            pickings |= negative_picking
        return pickings

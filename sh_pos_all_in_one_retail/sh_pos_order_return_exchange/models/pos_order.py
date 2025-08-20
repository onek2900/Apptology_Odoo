# Part of Softhealer Technologies.

from odoo import models, fields, api
from datetime import datetime, timedelta


class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    sh_return_qty = fields.Float(string="Return Qty.")
    sh_exchange_qty = fields.Float(string="Exchange Qty.")


class PosOrder(models.Model):
    _inherit = 'pos.order'

    is_return_order = fields.Boolean(string="Is Return Order?", readonly=True)
    is_exchange_order = fields.Boolean(
        string="Is Exchange Order?", readonly=True)
    old_pos_reference = fields.Char(string="Return Order", readonly=True)
    return_status = fields.Selection([
        ('nothing_return', 'Nothing Returned'),
        ('partialy_return', 'Partialy Returned'),
        ('fully_return', 'Fully Returned')
    ], string="Return Status ", default='nothing_return',
        readonly=True, copy=False, help="Return status of Order")
    total_return_order = fields.Integer(compute='_compute_return_order_total_', string="Total Return Order ",)
    total_exchange_order = fields.Integer(compute='_compute_exchange_order_total_', string="Total Exchange Order ",)

    def _compute_return_order_total_(self):
        for each in self:
            return_order = self.search_read(
                [('old_pos_reference', '=', each.pos_reference), ('is_return_order', '=', True)])
            each.total_return_order = len(return_order)

    def _compute_exchange_order_total_(self):

        for each in self:
            exchange_order = self.search_read(
                [('old_pos_reference', '=', each.pos_reference), ('is_exchange_order', '=', True)])
            each.total_exchange_order = len(exchange_order)

    @api.model
    def _order_fields(self, ui_order):

        res = super(PosOrder, self)._order_fields(ui_order)
        res['is_return_order'] = ui_order.get('is_return_order') if ui_order.get('is_return_order') else False
        res['is_exchange_order'] = ui_order.get('is_exchange_order') if ui_order.get('is_exchange_order') else False
        res['old_pos_reference'] = ui_order.get('old_pos_reference') if ui_order.get('old_pos_reference') else False

        for return_line in ui_order.get('lines'):
            if return_line[2].get('refunded_orderline_id'):
                refund_parent_order = self.browse(self.env['pos.order.line'].browse(
                    return_line[2]['refunded_orderline_id']).order_id.id)
                res['is_return_order'] = True
                res['old_pos_reference'] = refund_parent_order.pos_reference

        if ui_order.get('is_return_order'):
            flag = True
            parent_order = self.search(
                [('pos_reference', '=', ui_order['old_pos_reference'])], limit=1)
            updated_lines = ui_order['lines']

            for uptd in updated_lines:
                if uptd[2].get('old_sh_line_id'):
                    line = self.env['pos.order.line'].search([('order_id', '=', parent_order.id), ('id', '=', uptd[2]['old_sh_line_id'])], limit=1)
                    if line:
                        line.sh_return_qty += -(uptd[2]['qty'])
            if parent_order.lines:
                for line in parent_order.lines:
                    if flag:
                        if line.qty > line.sh_return_qty:
                            flag = False
            if flag:
                parent_order.return_status = 'fully_return'
            else:
                parent_order.return_status = 'partialy_return'

        if ui_order.get('is_exchange_order'):
            flag = True
            parent_order = self.search(
                [('pos_reference', '=', ui_order['old_pos_reference'])], limit=1)
            updated_lines = ui_order['lines']
            for uptd in updated_lines:
                if uptd[2].get('old_sh_line_id'):
                    line = self.env['pos.order.line'].search([('order_id', '=', parent_order.id),
                                                              ('id', '=', uptd[2]['old_sh_line_id'])], limit=1)
                    if line:
                        line.sh_return_qty += -(uptd[2]['qty'])
            if parent_order.lines:
                for line in parent_order.lines:
                    if flag:
                        if line.qty > line.sh_return_qty:
                            flag = False
            if flag:
                parent_order.return_status = 'fully_return'
            else:
                parent_order.return_status = 'partialy_return'

        return res

    @api.model
    def _process_order(self, order, draft, existing_order):
        order_id = super(PosOrder, self)._process_order(
            order, draft, existing_order)
        pos_order = self.search([('id', '=', order_id)])
        old_pos_order = self.search(
            [('pos_reference', '=', pos_order.old_pos_reference)])
        if old_pos_order:
            if pos_order.is_return_order:
                if old_pos_order.old_pos_reference:
                    old_pos_order.write(
                        {'old_pos_reference': old_pos_order.old_pos_reference + ' , ' + pos_order.pos_reference})
                else:
                    old_pos_order.write(
                        {'old_pos_reference': pos_order.pos_reference})
            if pos_order.is_exchange_order:
                if old_pos_order.old_pos_reference:
                    old_pos_order.write(
                        {'old_pos_reference': old_pos_order.old_pos_reference + ' , ' + pos_order.pos_reference})
                else:
                    old_pos_order.write(
                        {'old_pos_reference': pos_order.pos_reference})
        return order_id

    def action_view_return(self):
        return {
            'name': 'Return Order',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('old_pos_reference', '=', self.pos_reference), ('is_return_order', '=', True)],
            'res_model': 'pos.order',
            'target': 'current',
        }

    def action_view_exchange(self):
        return {
            'name': 'Exchange Order',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('old_pos_reference', '=', self.pos_reference), ('is_exchange_order', '=', True)],
            'res_model': 'pos.order',
            'target': 'current',
        }

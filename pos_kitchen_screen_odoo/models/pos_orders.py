# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models
from datetime import timedelta

_logger = logging.getLogger(__name__)



class PosOrder(models.Model):
    """Inheriting the pos order model"""
    _inherit = "pos.order"

    order_status = fields.Selection(string="Order Status",
                                    selection=[("draft", "Draft"),
                                               ("waiting", "Cooking"),
                                               ("ready", "Ready"),
                                               ("cancel", "Cancel")],
                                    default='draft',
                                    help='To know the status of order')

    @staticmethod
    def _normalize_bool(value):
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value)
        if isinstance(value, str):
            normalized = value.strip().lower()
            if not normalized:
                return False
            if normalized in {'false', '0', 'no', 'off', 'n'}:
                return False
            if normalized in {'true', '1', 'yes', 'on', 'y'}:
                return True
            return bool(value)
        if isinstance(value, (list, tuple, set)):
            return any(PosOrder._normalize_bool(v) for v in value)
        return bool(value)

    @staticmethod
    def _sanitize_new_line_summary(summary):
        sanitized = []
        if not summary:
            return sanitized
        for entry in summary:
            if not isinstance(entry, dict):
                continue
            quantity = entry.get('quantity')
            try:
                qty = float(quantity)
            except (TypeError, ValueError):
                qty = 0.0
            if qty <= 0:
                continue
            sanitized.append({
                'product_id': entry.get('product_id'),
                'product_name': (entry.get('product_name') or entry.get('name') or ''),
                'quantity': round(qty, 4),
                'note': entry.get('note') or '',
            })
        return sanitized

    @staticmethod
    def _calculate_new_line_count(summary):
        total = 0
        for entry in summary or []:
            try:
                qty = float(entry.get('quantity', 0))
            except (TypeError, ValueError):
                qty = 0.0
            if qty > 0:
                total += qty
        return round(total, 4)

    @api.model
    def _order_fields(self, ui_order):
        res = super()._order_fields(ui_order)
        lines = res.get('lines') or []
        ui_lines = ui_order.get('lines') or []

        def _get_ui_vals(index):
            if index >= len(ui_lines):
                return {}
            ui_line = ui_lines[index]
            if isinstance(ui_line, (list, tuple)) and len(ui_line) >= 3 and isinstance(ui_line[2], dict):
                return ui_line[2]
            return {}

        try:
            for idx, line_tuple in enumerate(lines):
                if not isinstance(line_tuple, (list, tuple)) or len(line_tuple) < 3:
                    continue
                line_vals = line_tuple[2]
                if not isinstance(line_vals, dict):
                    continue

                ui_vals = _get_ui_vals(idx)

                candidates = [
                    ui_vals.get('is_topping'),
                    ui_vals.get('sh_is_topping'),
                    line_vals.get('is_topping'),
                    line_vals.get('sh_is_topping'),
                ]
                flag = any(self._normalize_bool(val) for val in candidates)

                product_flag = False
                product_id = line_vals.get('product_id') or ui_vals.get('product_id')
                if isinstance(product_id, (list, tuple)):
                    product_id = product_id[0]
                if product_id:
                    product = self.env['product.product'].sudo().browse(product_id)
                    product_flag = bool(
                        getattr(product, 'is_topping', False)
                        or getattr(product, 'sh_is_topping', False)
                    )

                final_flag = flag or product_flag

                line_vals['sh_is_topping'] = final_flag
                line_vals['product_sh_is_topping'] = product_flag

                has_candidates = [
                    ui_vals.get('sh_is_has_topping'),
                    ui_vals.get('is_has_topping'),
                    line_vals.get('sh_is_has_topping'),
                    line_vals.get('is_has_topping'),
                ]
                has_flag = any(self._normalize_bool(val) for val in has_candidates)
                line_vals['sh_is_has_topping'] = has_flag

                _logger.debug('Normalized topping flags', {
                    'line_index': idx,
                    'product_id': product_id,
                    'product_flag': product_flag,
                    'ui_is_topping': ui_vals.get('is_topping'),
                    'ui_sh_is_topping': ui_vals.get('sh_is_topping'),
                    'final_flag': final_flag,
                    'has_topping': has_flag,
                })
        except Exception as exc:
            _logger.debug('Failed to normalize topping flags: %s', exc)

        return res

    order_ref = fields.Char(string="Order Reference",
                            help='Reference of the order')
    is_cooking = fields.Boolean(string="Is Cooking",
                                help='To identify the order is  kitchen orders')
    hour = fields.Char(string="Order Time", readonly=True,
                       help='To set the time of each order')
    minutes = fields.Char(string='order time')
    floor = fields.Char(string='Floor time')
    kitchen_new_line_summary = fields.Json(string='Kitchen New Line Summary', default=list)
    kitchen_new_line_count = fields.Float(string='Kitchen New Line Count', default=0.0)
    kitchen_send_logs = fields.Json(string='Kitchen Send Logs', default=list)


    def write(self, vals):
        """Super the write function for adding order status in vals"""
        message = {
            'res_model': self._name,
            'message': 'pos_order_created'
        }
        self.env["bus.bus"]._sendone('pos_order_created',
                                     "notification",
                                     message)
        for order in self:
            if order.order_status == "waiting" and vals.get(
                    "order_status") != "ready":
                vals["order_status"] = order.order_status
            if vals.get("state") and vals[
                "state"] == "paid" and order.name == "/":
                vals["name"] = self._compute_order_name()
        return super(PosOrder, self).write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        """Override create function for the validation of the order"""
        message = {
            'res_model': self._name,
            'message': 'pos_order_created'
        }
        self.env["bus.bus"]._sendone('pos_order_created',
                                     "notification",
                                     message)
        for vals in vals_list:
            pos_orders = self.search(
                [("pos_reference", "=", vals["pos_reference"])])
            if pos_orders:
                return super().create(vals_list)

            else:
                if vals.get('order_id') and not vals.get('name'):
                    # set name based on the sequence specified on the config
                    config = self.env['pos.order'].browse(
                        vals['order_id']).session_id.config_id
                    if config.sequence_line_id:
                        vals['name'] = config.sequence_line_id._next()
                if not vals.get('name'):
                    # fallback on any pos.order sequence
                    vals['name'] = self.env['ir.sequence'].next_by_code(
                        'pos.order.line')
                return super().create(vals_list)


    def get_details(self, shop_id, order=None):
        """For getting the kitchen orders for the cook"""
        order_record = self.env['pos.order']
        new_line_summary = []
        ticket_uid = None
        if order:
            payload = order[0].copy()
            new_line_summary = payload.pop('kitchen_new_lines', []) or []
            ticket_uid = payload.pop('ticket_uid', None)
            order_ref = payload.get('pos_reference')
            order_record = self.search([("pos_reference", "=", order_ref)])
            if not order_record:
                order_record = self.create([payload])
            else:
                order_record.lines = False
                order_record.write(payload)
            sanitized_summary = self._sanitize_new_line_summary(new_line_summary)
            if sanitized_summary and not ticket_uid:
                ticket_uid = sanitized_summary[0].get('ticket_uid')
            ticket_uid = ticket_uid or f"ticket_{order_ref or ''}_{fields.Datetime.now().timestamp()}"
            ticket_lines = order_record.lines.filtered(lambda l: l.kitchen_ticket_uid == ticket_uid)
            line_snapshot = []
            for line in ticket_lines:
                line_snapshot.append({
                    'line_id': line.id,
                    'product_id': line.product_id.id,
                    'full_product_name': line.full_product_name,
                    'qty': line.qty,
                    'note': line.note,
                    'order_status': line.order_status,
                })
            logs = list(order_record.kitchen_send_logs or [])
            if ticket_lines:
                logs.append({
                    'ticket_uid': ticket_uid,
                    'created_at': fields.Datetime.now().isoformat(),
                    'line_ids': ticket_lines.ids,
                    'line_snapshot': line_snapshot,
                    'line_count': self._calculate_new_line_count(sanitized_summary) or sum(line.qty for line in ticket_lines),
                })
            order_record.write({
                'kitchen_new_line_summary': sanitized_summary,
                'kitchen_new_line_count': self._calculate_new_line_count(sanitized_summary),
                'kitchen_send_logs': logs,
            })
        kitchen_screen = self.env["kitchen.screen"].sudo().search([("pos_config_id", "=", shop_id)])
    
        pos_session_id = self.env["pos.session"].search([('config_id', '=', shop_id), ('state', '=', 'opened')], limit=1)
    
        pos_orders = self.env["pos.order"].search(
            ["&", ("lines.is_cooking", "=", True),
             ("lines.product_id.pos_categ_ids", "in",
              kitchen_screen.pos_categ_ids.ids), ('session_id', '=', pos_session_id.id)], order="date_order")
        values = {"orders": pos_orders.read(), "order_lines": pos_orders.lines.read()}
        return values
    
        @api.model
        def get_order_details(self, screen_id):
            kitchen_screen = self.env["kitchen.screen"].sudo().browse(int(screen_id))
    
            pos_session_id = self.env["pos.session"].search([
                ('config_id', '=', kitchen_screen.pos_config_id.id),
                ('state', '=', 'opened')], limit=1)
    
            pos_orders = self.env["pos.order"].search(
                ["&", ("lines.is_cooking", "=", True),
                 ("lines.product_id.pos_categ_ids", "in", kitchen_screen.pos_categ_ids.ids),
                 ('session_id', '=', pos_session_id.id)], order="date_order")
            values = {"orders": pos_orders.read()}
            return values
    
    
        def action_pos_order_paid(self):
            """Supering the action_pos_order_paid function for setting its kitchen
            order and setting the order reference"""
            res = super().action_pos_order_paid()
            kitchen_screen = self.env["kitchen.screen"].search(
                [("pos_config_id", "=", self.config_id.id)]
            )
            for order_line in self.lines:
                order_line.is_cooking = True
            if kitchen_screen:
                for line in self.lines:
                    line.is_cooking = True
                self.is_cooking = True
                self.order_ref = self.name
            return res
    
        @api.onchange("order_status")
        def onchange_order_status(self):
            """To set is_cooking false"""
            if self.order_status == "ready":
                self.is_cooking = False
    
        def order_progress_draft(self):
            """Calling function from js to change the order status"""
            self.order_status = "waiting"
            for line in self.lines:
                if line.order_status != "ready":
                    line.order_status = "waiting"
    
        def order_progress_cancel(self):
            """Calling function from js to change the order status"""
            vals = {'order_status': 'cancel'}
            if 'online_order_status' in self._fields:
                vals['online_order_status'] = 'cancelled'
            if 'declined_time' in self._fields:
                vals['declined_time'] = fields.Datetime.now()
            self.write(vals)
            self.write({
                'kitchen_new_line_summary': [],
                'kitchen_new_line_count': 0,
            })
    
            for line in self.lines:
                if line.order_status != "ready":
                    line.order_status = "cancel"
            if hasattr(self, 'update_order_status_in_deliverect'):
                self.update_order_status_in_deliverect(110)
    
            deliverect_payment_method = False
            payment_method_model = self.env['pos.payment.method']
            if 'is_deliverect_payment_method' in payment_method_model._fields:
                deliverect_payment_method = payment_method_model.search([
                    ('company_id', '=', self.company_id.id),
                    ('is_deliverect_payment_method', '=', True)
                ], limit=1)
            if deliverect_payment_method:
                refund_action = self.refund()
                refund = self.env['pos.order'].sudo().browse(refund_action['res_id'])
                payment_context = {"active_ids": refund.ids, "active_id": refund.id}
                refund_payment = self.env['pos.make.payment'].sudo().with_context(**payment_context).create({
                    'amount': refund.amount_total,
                    'payment_method_id': deliverect_payment_method.id,
                })
                refund_payment.with_context(**payment_context).check()
                self.env['pos.order'].sudo().browse(refund.id).action_pos_order_invoice()
    
        def order_progress_change(self):
            """Update the order status based on the progress of main (non modifier) lines."""
            kitchen_screen = self.env["kitchen.screen"].search([("pos_config_id", "=", self.config_id.id)])
            tracked_categories = kitchen_screen.pos_categ_ids
            relevant_lines = self.lines
            if tracked_categories:
                relevant_lines = relevant_lines.filtered(
                    lambda l: bool(l.product_id.pos_categ_ids & tracked_categories)
                )
            if not relevant_lines:
                relevant_lines = self.lines
    
            def _is_modifier(line):
                product = line.product_id
                return bool(
                    getattr(product, "is_topping", False)
                    or getattr(product, "sh_is_topping", False)
                    or getattr(line, "is_topping", False)
                    or getattr(line, "sh_is_topping", False)
                    or getattr(line, "product_sh_is_topping", False)
                )
    
            main_lines = relevant_lines.filtered(lambda l: not _is_modifier(l))
            if not main_lines:
                main_lines = relevant_lines
    
            pending_states = {"draft", "waiting"}
            ready_like_states = {"ready", "cancel"}
    
            new_status = self.order_status
            if any(line.order_status in pending_states for line in main_lines):
                new_status = "waiting"
            elif main_lines and all(line.order_status in ready_like_states for line in main_lines):
                new_status = "ready"
    
            if new_status != self.order_status:
                self.order_status = new_status
    
            if self.order_status == "ready":
                self.write({
                    'kitchen_new_line_summary': [],
                    'kitchen_new_line_count': 0,
                })
                if hasattr(self, 'update_order_status_in_deliverect'):
                    self.update_order_status_in_deliverect(70)
    
        @api.model
        def check_order(self, order_name):
            """Calling function from js to know status of the order"""
            pos_order = self.env['pos.order'].sudo().search(
                [('pos_reference', '=', str(order_name))])
            kitchen_order = self.env['kitchen.screen'].sudo().search(
                [('pos_config_id', '=', pos_order.config_id.id)])
            if kitchen_order:
                for category in pos_order.lines.mapped('product_id').mapped(
                        'pos_categ_ids').mapped('id'):
                    if category not in kitchen_order.pos_categ_ids.mapped('id'):
                        return {
                            'category': pos_order.lines.product_id.pos_categ_ids.browse(
                                category).name}
            if kitchen_order and pos_order:
                if pos_order.order_status != 'ready':
                    return True
                else:
                    return False
            else:
                return False
    
        @api.model
        def check_order_status(self, order_name):
            pos_order = self.env['pos.order'].sudo().search(
                [('pos_reference', '=', str(order_name))])
            kitchen_order = self.env['kitchen.screen'].sudo().search(
                [('pos_config_id', '=', pos_order.config_id.id)])
            for category in pos_order.lines.mapped('product_id').mapped(
                    'pos_categ_ids').mapped('id'):
                if category not in kitchen_order.pos_categ_ids.mapped('id'):
                    return 'no category'
            if kitchen_order:
                if pos_order.order_status == 'ready':
                    return False
                else:
                    return True
            else:
                return True
    
    
class PosOrderLine(models.Model):
    """Inheriting the pos order line"""
    _inherit = "pos.order.line"

    order_status = fields.Selection(
        selection=[('draft', 'Draft'), ('waiting', 'Cooking'),
                   ('ready', 'Ready'), ('cancel', 'Cancel')], default='draft',
        help='The status of orderliness')
    order_ref = fields.Char(related='order_id.order_ref',
                            string='Order Reference',
                            help='Order reference of order')
    kitchen_ticket_uid = fields.Char(string='Kitchen Ticket UID', copy=False)
    is_cooking = fields.Boolean(string="Cooking", default=False,
                                help='To identify the order is  '
                                     'kitchen orders')
    customer_id = fields.Many2one('res.partner', string="Customer",
                                  related='order_id.partner_id',
                                  help='Id of the customer')
    # Kitchen module relies on sh_is_topping on lines for grouping.


    product_sh_is_topping = fields.Boolean(string='Product Is Topping', default=False, help='Denormalized product topping flag for kitchen fallback')


    def get_product_details(self, ids):
        """To get the product details"""
        lines = self.env['pos.order'].browse(ids)
        res = []
        for rec in lines:
            res.append({
                'product_id': rec.product_id.id,
                'name': rec.product_id.name,
                'qty': rec.qty
            })
        return res

    def order_progress_change(self):
        """Calling function from js to change the order_line status"""
        for line in self:
            if line.order_status == 'ready':
                line.order_status = 'waiting'
            else:
                line.order_status = 'ready'
    

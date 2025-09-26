"""POS Kitchen: model extensions for orders and lines.

This module extends pos.order and pos.order.line with kitchen tracking fields
and behaviors used by the kitchen and order tracking screens.
"""

import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class PosKitchenTicket(models.Model):
    _name = "pos.kitchen.ticket"
    _description = "Kitchen ticket per press"

    order_id = fields.Many2one("pos.order", required=True, ondelete="cascade", index=True)
    line_ids = fields.Many2many("pos.order.line", string="Lines")
    press_index = fields.Integer(string="Press Index", default=0, index=True)
    ticket_uid = fields.Char(string="Ticket UID", index=True)
    created_at = fields.Datetime(string="Created At", default=fields.Datetime.now)
    state = fields.Selection([
        ("inprogress", "In Progress"),
        ("completed", "Completed"),
    ], compute="_compute_state")

    def _compute_state(self):
        for rec in self:
            mains = rec.line_ids.filtered(lambda l: not getattr(l, "product_sh_is_topping", False) and not getattr(l, "sh_is_topping", False))
            rec.state = "completed" if (mains and all(l.order_status == "ready" for l in mains)) else "inprogress"


class PosOrder(models.Model):
    _inherit = "pos.order"

    # Fields
    order_status = fields.Selection(
        selection=[("draft", "Draft"), ("waiting", "Cooking"), ("ready", "Ready"), ("cancel", "Cancel")],
        string="Order Status",
        default="draft",
        help="To know the status of order",
    )
    order_ref = fields.Char(string="Order Reference", help="Reference of the order")
    is_cooking = fields.Boolean(string="Is Cooking", help="Identify kitchen orders")
    hour = fields.Char(string="Order Time", readonly=True)
    minutes = fields.Char(string="order time")
    floor = fields.Char(string="Floor time")
    # Legacy fields removed: kitchen_new_line_summary, kitchen_new_line_count, kitchen_send_logs
    # Press counter: increments each time order is sent to kitchen; starts at 0
    kitchen_press_index = fields.Integer(string="Kitchen Press Index", default=0, help="0-based counter of sends to kitchen")

    # Helpers
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
            if normalized in {"false", "0", "no", "off", "n"}:
                return False
            if normalized in {"true", "1", "yes", "on", "y"}:
                return True
            return bool(value)
        if isinstance(value, (list, tuple, set)):
            return any(PosOrder._normalize_bool(v) for v in value)
        return bool(value)

    # Removed legacy helpers _sanitize_new_line_summary and _calculate_new_line_count

    # Overrides
    @api.model
    def _order_fields(self, ui_order):
        res = super()._order_fields(ui_order)
        lines = res.get("lines") or []
        ui_lines = ui_order.get("lines") or []

        def _get_ui_vals(i):
            if i >= len(ui_lines):
                return {}
            u = ui_lines[i]
            return u[2] if isinstance(u, (list, tuple)) and len(u) >= 3 and isinstance(u[2], dict) else {}

        try:
            for i, lt in enumerate(lines):
                if not isinstance(lt, (list, tuple)) or len(lt) < 3:
                    continue
                lv = lt[2]
                if not isinstance(lv, dict):
                    continue
                uv = _get_ui_vals(i)
                flag = any(
                    self._normalize_bool(v)
                    for v in [uv.get("is_topping"), uv.get("sh_is_topping"), lv.get("is_topping"), lv.get("sh_is_topping")]
                )
                pid = lv.get("product_id") or uv.get("product_id")
                if isinstance(pid, (list, tuple)):
                    pid = pid[0]
                pflag = False
                if pid:
                    p = self.env["product.product"].sudo().browse(pid)
                    pflag = bool(getattr(p, "is_topping", False) or getattr(p, "sh_is_topping", False))
                lv["sh_is_topping"] = flag or pflag
                lv["product_sh_is_topping"] = pflag
                has = any(
                    self._normalize_bool(v)
                    for v in [uv.get("sh_is_has_topping"), uv.get("is_has_topping"), lv.get("sh_is_has_topping"), lv.get("is_has_topping")]
                )
                lv["sh_is_has_topping"] = has
        except Exception as exc:
            _logger.debug("Failed to normalize topping flags: %s", exc)
        return res

    def write(self, vals):
        # Avoid spamming kitchen bus on every write; a single notification is
        # sent explicitly from flows that persist kitchen sends (e.g., get_details).
        for order in self:
            if order.order_status == "waiting" and vals.get("order_status") != "ready":
                vals["order_status"] = order.order_status
            if vals.get("state") and vals["state"] == "paid" and order.name == "/":
                vals["name"] = self._compute_order_name()
        return super(PosOrder, self).write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        # Do not emit kitchen bus from generic create path; handled by callers that
        # change kitchen-visible state (e.g., get_details).
        for vals in vals_list:
            pos_orders = self.search([("pos_reference", "=", vals.get("pos_reference"))])
            if pos_orders:
                return super().create(vals_list)
            if vals.get("order_id") and not vals.get("name"):
                config = self.env["pos.order"].browse(vals["order_id"]).session_id.config_id
                if config.sequence_line_id:
                    vals["name"] = config.sequence_line_id._next()
            if not vals.get("name"):
                vals["name"] = self.env["ir.sequence"].next_by_code("pos.order.line")
        return super().create(vals_list)

    # Kitchen helpers and transitions
    def get_details(self, shop_id, order=None):
        order_record = self.env["pos.order"]
        if order:
            # Minimal upsert of order/lines and create a per-press kitchen ticket
            payload = order[0].copy()
            ticket_uid = payload.pop("ticket_uid", None)
            payload.pop("kitchen_new_lines", None)
            order_ref = payload.get("pos_reference")
            order_record = self.search([("pos_reference", "=", order_ref)])
            if not order_record:
                # First press: create order with provided lines as-is
                order_record = self.create([payload])
            else:
                # Existing order: append only the lines belonging to this press (by ticket_uid)
                all_cmds = payload.get("lines") or []
                press_cmds = []
                for cmd in all_cmds:
                    try:
                        vals = isinstance(cmd, (list, tuple)) and len(cmd) >= 3 and isinstance(cmd[2], dict) and cmd[2] or None
                        if not vals:
                            continue
                        if ticket_uid and str(vals.get("kitchen_ticket_uid") or "") != str(ticket_uid):
                            continue
                        press_cmds.append((0, 0, vals))
                    except Exception:
                        continue
                write_vals = {}
                # Append new lines for this press only
                if press_cmds:
                    write_vals["lines"] = press_cmds
                # Update simple order fields (exclude lines so we don't overwrite existing)
                for k in ["order_status", "is_cooking", "order_ref", "hour", "minutes", "floor", "session_id", "config_id", "table_id"]:
                    if k in payload:
                        write_vals[k] = payload[k]
                if write_vals:
                    order_record.write(write_vals)
            # Create/update kitchen ticket for this send
            if ticket_uid:
                ticket_lines = order_record.lines.filtered(lambda l: str(getattr(l, "kitchen_ticket_uid", "")) == str(ticket_uid))
                # Only create a ticket when there are actual lines for this press
                if ticket_lines:
                    existing = self.env["pos.kitchen.ticket"].sudo().search([("order_id", "=", order_record.id)])
                    press_index = len(existing)
                    kt = self.env["pos.kitchen.ticket"].sudo().search([("ticket_uid", "=", ticket_uid), ("order_id", "=", order_record.id)], limit=1)
                    vals = {
                        "order_id": order_record.id,
                        "press_index": press_index,
                        "ticket_uid": ticket_uid,
                        "created_at": fields.Datetime.now(),
                    }
                    if kt:
                        kt.write(vals)
                    else:
                        kt = self.env["pos.kitchen.ticket"].sudo().create(vals)
                    kt.write({"line_ids": [(6, 0, ticket_lines.ids)]})
        kitchen_screen = self.env["kitchen.screen"].sudo().search([("pos_config_id", "=", shop_id)])
        pos_session_id = self.env["pos.session"].search([("config_id", "=", shop_id), ("state", "=", "opened")], limit=1)
        pos_orders = self.env["pos.order"].search(
            [
                "&",
                ("lines.is_cooking", "=", True),
                ("lines.product_id.pos_categ_ids", "in", kitchen_screen.pos_categ_ids.ids),
                ("session_id", "=", pos_session_id.id),
            ],
            order="date_order",
        )
        # Collect tickets for these orders
        tickets = self.env["pos.kitchen.ticket"].sudo().search([("order_id", "in", pos_orders.ids)])
        # After persisting/updating, notify kitchen screens once.
        try:
            message = {"res_model": self._name, "message": "pos_order_created"}
            self.env["bus.bus"]._sendone("pos_order_created", "notification", message)
        except Exception:
            pass
        return {
            "orders": pos_orders.read(),
            "order_lines": pos_orders.lines.read(),
            "tickets": tickets.read(["id", "order_id", "line_ids", "press_index", "ticket_uid", "created_at", "state"]),
        }

    def action_pos_order_paid(self):
        res = super().action_pos_order_paid()
        kitchen_screen = self.env["kitchen.screen"].search([("pos_config_id", "=", self.config_id.id)])
        for l in self.lines:
            l.is_cooking = True
        if kitchen_screen:
            for l in self.lines:
                l.is_cooking = True
            self.is_cooking = True
            self.order_ref = self.name
        return res

    @api.onchange("order_status")
    def onchange_order_status(self):
        if self.order_status == "ready":
            self.is_cooking = False

    def order_progress_draft(self):
        self.order_status = "waiting"
        for l in self.lines:
            if l.order_status != "ready":
                l.order_status = "waiting"

    def order_progress_cancel(self):
        vals = {"order_status": "cancel"}
        if "online_order_status" in self._fields:
            vals["online_order_status"] = "cancelled"
        if "declined_time" in self._fields:
            vals["declined_time"] = fields.Datetime.now()
        self.write(vals)
        # Removed clearing of legacy kitchen delta fields
        for l in self.lines:
            if l.order_status != "ready":
                l.order_status = "cancel"
        if hasattr(self, "update_order_status_in_deliverect"):
            self.update_order_status_in_deliverect(110)
        pm_model = self.env["pos.payment.method"]
        method = False
        if "is_deliverect_payment_method" in pm_model._fields:
            method = pm_model.search(
                [("company_id", "=", self.company_id.id), ("is_deliverect_payment_method", "=", True)], limit=1
            )
        if method:
            refund_action = self.refund()
            refund = self.env["pos.order"].sudo().browse(refund_action["res_id"])
            ctx = {"active_ids": refund.ids, "active_id": refund.id}
            payment = (
                self.env["pos.make.payment"].sudo().with_context(**ctx).create(
                    {"amount": refund.amount_total, "payment_method_id": method.id}
                )
            )
            payment.with_context(**ctx).check()
            self.env["pos.order"].sudo().browse(refund.id).action_pos_order_invoice()

    def order_progress_change(self):
        ks = self.env["kitchen.screen"].search([("pos_config_id", "=", self.config_id.id)])
        tracked = ks.pos_categ_ids
        rel = self.lines
        if tracked:
            rel = rel.filtered(lambda l: bool(l.product_id.pos_categ_ids & tracked))
        if not rel:
            rel = self.lines
        def _is_modifier(line):
            p = line.product_id
            return bool(
                getattr(p, "is_topping", False)
                or getattr(p, "sh_is_topping", False)
                or getattr(line, "is_topping", False)
                or getattr(line, "sh_is_topping", False)
                or getattr(line, "product_sh_is_topping", False)
            )
        mains = rel.filtered(lambda l: not _is_modifier(l)) or rel
        pending = {"draft", "waiting"}
        ready_like = {"ready", "cancel"}
        new = self.order_status
        if any(l.order_status in pending for l in mains):
            new = "waiting"
        elif mains and all(l.order_status in ready_like for l in mains):
            new = "ready"
        if new != self.order_status:
            self.order_status = new
        if self.order_status == "ready":
            # Explicitly stop tracking in kitchen once ready
            # 1) Mark all main lines as ready so UI derives READY status from lines
            mains_filtered = mains.filtered(lambda l: l.order_status != "ready") if mains else self.lines.filtered(lambda l: l.order_status != "ready")
            if mains_filtered:
                mains_filtered.write({"order_status": "ready"})
            # 2) Turn off cooking flags on lines and order so fetch domain drops them
            self.lines.write({"is_cooking": False})
            self.write({
                "is_cooking": False,
            })
            if hasattr(self, "update_order_status_in_deliverect"):
                self.update_order_status_in_deliverect(70)

    @api.model
    def check_order(self, order_name=None, *args, **kwargs):
        # Accept extra positional args to be resilient to various call_kw signatures
        if order_name is None and args:
            order_name = args[0]
        if order_name is None:
            return False
        pos_order = self.env["pos.order"].sudo().search([("pos_reference", "=", str(order_name))])
        kitchen_order = self.env["kitchen.screen"].sudo().search([("pos_config_id", "=", pos_order.config_id.id)])
        if kitchen_order:
            for category in (
                pos_order.lines.mapped("product_id").mapped("pos_categ_ids").mapped("id")
            ):
                if category not in kitchen_order.pos_categ_ids.mapped("id"):
                    return {"category": pos_order.lines.product_id.pos_categ_ids.browse(category).name}
        if kitchen_order and pos_order:
            return pos_order.order_status != "ready"
        return False

    @api.model
    def check_order_status(self, order_name=None, *args, **kwargs):
        # Accept extra positional args to be resilient to various call_kw signatures
        if order_name is None and args:
            order_name = args[0]
        if order_name is None:
            return True
        pos_order = self.env["pos.order"].sudo().search([("pos_reference", "=", str(order_name))])
        kitchen_order = self.env["kitchen.screen"].sudo().search([("pos_config_id", "=", pos_order.config_id.id)])
        for category in pos_order.lines.mapped("product_id").mapped("pos_categ_ids").mapped("id"):
            if category not in kitchen_order.pos_categ_ids.mapped("id"):
                return "no category"
        if kitchen_order:
            return pos_order.order_status != "ready"
        return True


class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    order_status = fields.Selection(
        selection=[("draft", "Draft"), ("waiting", "Cooking"), ("ready", "Ready"), ("cancel", "Cancel")],
        default="draft",
        help="The status of orderliness",
    )
    order_ref = fields.Char(related="order_id.order_ref", string="Order Reference", help="Order reference of order")
    kitchen_ticket_uid = fields.Char(string="Kitchen Ticket UID", copy=False)
    is_cooking = fields.Boolean(string="Cooking", default=False, help="Identify kitchen orders")
    customer_id = fields.Many2one("res.partner", string="Customer", related="order_id.partner_id")
    product_sh_is_topping = fields.Boolean(
        string="Product Is Topping", default=False, help="Denormalized product topping flag"
    )

    def get_product_details(self, ids):
        lines = self.env["pos.order"].browse(ids)
        res = []
        for rec in lines:
            res.append({"product_id": rec.product_id.id, "name": rec.product_id.name, "qty": rec.qty})
        return res

    def order_progress_change(self):
        for line in self:
            line.order_status = "waiting" if line.order_status == "ready" else "ready"

"""POS Kitchen: model extensions for orders and lines.

This module extends pos.order and pos.order.line with kitchen tracking fields
and behaviors used by the kitchen and order tracking screens.
"""

import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


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
    kitchen_new_line_summary = fields.Json(string="Kitchen New Line Summary", default=list)
    kitchen_new_line_count = fields.Float(string="Kitchen New Line Count", default=0.0)
    kitchen_send_logs = fields.Json(string="Kitchen Send Logs", default=list)
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

    @staticmethod
    def _sanitize_new_line_summary(summary):
        out = []
        for e in summary or []:
            if not isinstance(e, dict):
                continue
            try:
                qty = float(e.get("quantity"))
            except (TypeError, ValueError):
                qty = 0.0
            if qty <= 0:
                continue
            out.append(
                {
                    "product_id": e.get("product_id"),
                    "product_name": (e.get("product_name") or e.get("name") or ""),
                    "quantity": round(qty, 4),
                    "note": e.get("note") or "",
                }
            )
        return out

    @staticmethod
    def _calculate_new_line_count(summary):
        total = 0
        for e in summary or []:
            try:
                qty = float(e.get("quantity", 0))
            except (TypeError, ValueError):
                qty = 0.0
            if qty > 0:
                total += qty
        return round(total, 4)

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
        message = {"res_model": self._name, "message": "pos_order_created"}
        self.env["bus.bus"]._sendone("pos_order_created", "notification", message)
        for order in self:
            if order.order_status == "waiting" and vals.get("order_status") != "ready":
                vals["order_status"] = order.order_status
            if vals.get("state") and vals["state"] == "paid" and order.name == "/":
                vals["name"] = self._compute_order_name()
        return super(PosOrder, self).write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        message = {"res_model": self._name, "message": "pos_order_created"}
        self.env["bus.bus"]._sendone("pos_order_created", "notification", message)
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
        new_line_summary = []
        ticket_uid = None
        if order:
            payload = order[0].copy()
            new_line_summary = payload.pop("kitchen_new_lines", []) or []
            ticket_uid = payload.pop("ticket_uid", None)
            order_ref = payload.get("pos_reference")
            order_record = self.search([("pos_reference", "=", order_ref)])
            if not order_record:
                order_record = self.create([payload])
            else:
                order_record.lines = False
                order_record.write(payload)
            sanitized = self._sanitize_new_line_summary(new_line_summary)
            if sanitized and not ticket_uid:
                ticket_uid = sanitized[0].get("ticket_uid")
            ticket_uid = ticket_uid or f"ticket_{order_ref or ''}_{fields.Datetime.now().timestamp()}"
            ticket_lines = order_record.lines.filtered(lambda l: l.kitchen_ticket_uid == ticket_uid)
            snap = [
                {
                    "line_id": l.id,
                    "product_id": l.product_id.id,
                    "full_product_name": l.full_product_name,
                    "qty": l.qty,
                    "note": l.note,
                    "order_status": l.order_status,
                }
                for l in ticket_lines
            ]
            logs = list(order_record.kitchen_send_logs or [])
            # Current press index is the number of existing logs (0-based)
            current_press_index = len(logs)
            if ticket_lines:
                logs.append(
                    {
                        "ticket_uid": ticket_uid,
                        "created_at": fields.Datetime.now().isoformat(),
                        "line_ids": ticket_lines.ids,
                        "line_snapshot": snap,
                        "line_count": self._calculate_new_line_count(sanitized) or sum(l.qty for l in ticket_lines),
                        "press_index": current_press_index,
                    }
                )
            order_record.write(
                {
                    "kitchen_new_line_summary": sanitized,
                    "kitchen_new_line_count": self._calculate_new_line_count(sanitized),
                    "kitchen_send_logs": logs,
                    "kitchen_press_index": current_press_index,
                }
            )
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
        return {"orders": pos_orders.read(), "order_lines": pos_orders.lines.read()}

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
        self.write({"kitchen_new_line_summary": [], "kitchen_new_line_count": 0})
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
                "kitchen_new_line_summary": [],
                "kitchen_new_line_count": 0,
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

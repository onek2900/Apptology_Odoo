# Copyright (C) Softhealer Technologies.
# Part of Softhealer Technologies.

from odoo import models

class POSOrder(models.Model):
    _name = 'pos.order'
    _inherit = ['pos.order', 'portal.mixin',
                'mail.thread', 'mail.activity.mixin',
                'utm.mixin']

    def _compute_access_url(self):
        res = super()._compute_access_url()
        for order in self:
            order.access_url = '/my/pos/%s' % (order.id)
        return res

    def _get_report_base_filename(self):
        self.ensure_one()
        return '%s %s' % ('Receipt', self.name)

    def _get_portal_return_action(self):
        """
        Return the action used to display orders
        when returning from customer portal.
        """
        self.ensure_one()
        return self.env.ref('point_of_sale.action_pos_pos_form')

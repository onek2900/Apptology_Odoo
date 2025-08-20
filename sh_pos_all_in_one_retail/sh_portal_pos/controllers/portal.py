# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from collections import OrderedDict
from dateutil.relativedelta import relativedelta
from operator import itemgetter

from odoo import fields, http, _
from odoo.http import request
from odoo.tools import date_utils, groupby as groupbyelem
from odoo.osv.expression import AND

from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError
import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class ShPOSCustomerPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        """Get and Set Count in My Account page"""
        values = super()._prepare_home_portal_values(counters)
        pos_obj = request.env['pos.order']
        pos_count = pos_obj.sudo().search_count(
            [('partner_id', '=', request.env.user.partner_id.id)])
        if pos_count == 0:
            pos_count ='0'
            values['pos_count'] = pos_count
        else:
            values['pos_count'] = pos_count

        return values

    @http.route(['/my/pos', '/my/pos/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_pos(self, page=1, sortby=None, filterby=None, search=None, search_in='all', groupby='none', **kw):
        """POS List View With different filters and group by and search bar for search direct also"""
        POS_sudo = request.env['pos.order'].sudo()
        values = self._prepare_portal_layout_values()
        searchbar_sortings = {
            'date_order': {'label': _('Newest'), 'order': 'date_order desc'},
            'name': {'label': _('Name'), 'order': 'name'},
        }
        searchbar_inputs = {
            'all': {'input': 'all', 'label': _('Search in All')},
        }

        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'session': {'input': 'session', 'label': _('Session')},
            'user': {'input': 'user', 'label': _('User')},
            'status': {'input': 'status', 'label': _('Status')},
        }

        today = fields.Date.today()
        quarter_start, quarter_end = date_utils.get_quarter(today)
        last_week = today + relativedelta(weeks=-1)
        last_month = today + relativedelta(months=-1)
        last_year = today + relativedelta(years=-1)
        today_date_start = str(today) + " 00:00:00"
        today_date_end = str(today) + " 23:59:59"
        start_date = datetime.datetime.strptime(today_date_start, DEFAULT_SERVER_DATETIME_FORMAT)
        end_date = datetime.datetime.strptime(today_date_end, DEFAULT_SERVER_DATETIME_FORMAT)
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'today': {'label': _('Today'), 'domain': [("date_order", ">=", start_date),('date_order','<=',end_date)]},
            'week': {'label': _('This week'), 'domain': [('date_order', '>=', date_utils.start_of(today, "week")), ('date_order', '<=', date_utils.end_of(today, 'week'))]},
            'month': {'label': _('This month'), 'domain': [('date_order', '>=', date_utils.start_of(today, 'month')), ('date_order', '<=', date_utils.end_of(today, 'month'))]},
            'year': {'label': _('This year'), 'domain': [('date_order', '>=', date_utils.start_of(today, 'year')), ('date_order', '<=', date_utils.end_of(today, 'year'))]},
            'quarter': {'label': _('This Quarter'), 'domain': [('date_order', '>=', quarter_start), ('date_order', '<=', quarter_end)]},
            'last_week': {'label': _('Last week'), 'domain': [('date_order', '>=', date_utils.start_of(last_week, "week")), ('date_order', '<=', date_utils.end_of(last_week, 'week'))]},
            'last_month': {'label': _('Last month'), 'domain': [('date_order', '>=', date_utils.start_of(last_month, 'month')), ('date_order', '<=', date_utils.end_of(last_month, 'month'))]},
            'last_year': {'label': _('Last year'), 'domain': [('date_order', '>=', date_utils.start_of(last_year, 'year')), ('date_order', '<=', date_utils.end_of(last_year, 'year'))]},
        }
        # default sort by value
        if not sortby:
            sortby = 'date_order'
        order = searchbar_sortings[sortby]['order']
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain = AND([searchbar_filters[filterby]['domain']])

        if search and search_in:
            domain = AND([domain, [('name', 'ilike', search)]])
        domain = AND(
            [domain, [('partner_id', '=', request.env.user.partner_id.id)]])
        pos_count = POS_sudo.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/pos",
            url_args={'sortby': sortby, 'search_in': search_in,
                      'search': search, 'filterby': filterby},
            total=pos_count,
            page=page,
            step=self._items_per_page
        )

        if groupby == 'session':
            order = "session_id, %s" % order
        elif groupby == 'user':
            order = "user_id, %s" % order
        elif groupby == 'status':
            order = "state, %s" % order
        pos_orders = POS_sudo.search(
            domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        if groupby == 'session':
            grouped_orders = [POS_sudo.concat(
                *g) for k, g in groupbyelem(pos_orders, itemgetter('session_id'))]
        elif groupby == 'user':
            grouped_orders = [POS_sudo.concat(
                *g) for k, g in groupbyelem(pos_orders, itemgetter('user_id'))]
        elif groupby == 'status':
            grouped_orders = [POS_sudo.concat(
                *g) for k, g in groupbyelem(pos_orders, itemgetter('state'))]
        else:
            grouped_orders = [pos_orders]
        values.update({
            'pos_orders': pos_orders,
            'grouped_orders': grouped_orders,
            'page_name': 'pos',
            'default_url': '/my/pos',
            'pos_count': pos_count,
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'search_in': search_in,
            'sortby': sortby,
            'groupby': groupby,
            'searchbar_inputs': searchbar_inputs,
            'searchbar_groupby': searchbar_groupby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
        })
        return request.render("sh_pos_all_in_one_retail.portal_my_pos", values)

    @http.route(['/my/pos/<int:pos_id>'], type='http', auth="public", website=True)
    def portal_my_pos_form(self, pos_id, report_type=None, access_token=None, message=False, download=False, **kw):
        """POS Form View where you can download report and send messages also"""
        try:
            POS_sudo = self._document_check_access(
                'pos.order', pos_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(model=POS_sudo, report_type=report_type, report_ref='sh_pos_all_in_one_retail.action_report_pos_receipt', download=download)

        values = {
            'token': access_token,
            'pos_order': POS_sudo,
            'message': message,
            'bootstrap_formatting': True,
            'action': POS_sudo._get_portal_return_action(),
            'partner_id': POS_sudo.partner_id.id,
            'report_type': 'html',
        }
        return request.render('sh_pos_all_in_one_retail.portal_pos_form_template', values)

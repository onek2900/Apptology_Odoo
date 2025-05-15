# -*- coding: utf-8 -*-
from . import controllers
from . import models
from . import wizards


def post_init_hook(env):
    all_companies = env['res.company'].search([])

    for company in all_companies:
        journal = env['account.journal'].search([
            ('type', '=', 'bank'),
            ('company_id', '=', company.id)
        ], limit=1)
        if not journal and company.parent_id:
            journal = env['account.journal'].search([
                ('type', '=', 'bank'),
                ('company_id', '=', company.parent_id.id)
            ], limit=1)
        if journal:
            env['pos.payment.method'].sudo().create({
                'name': 'Deliverect',
                'journal_id': journal.id,
                'company_id': company.id,
                'is_deliverect_payment_method': True,
            })


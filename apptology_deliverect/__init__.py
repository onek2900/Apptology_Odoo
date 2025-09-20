# -*- coding: utf-8 -*-
from . import controllers
from . import models
from . import wizards


def post_init_hook(env):
    all_companies = env['res.company'].search([])

    for company in all_companies:
        # Ensure a Deliverect pricelist exists per company
        try:
            pricelist_model = env['product.pricelist'].sudo()
            deliverect_pricelist = pricelist_model.search([
                ('company_id', '=', company.id),
                ('is_deliverect_pricelist', '=', True)
            ], limit=1)
            if not deliverect_pricelist:
                pricelist_model.create({
                    'name': 'Deliverect',
                    'company_id': company.id,
                    'currency_id': company.currency_id.id,
                    'is_deliverect_pricelist': True,
                })
        except Exception:
            # If fields are not yet loaded during hook or any issue occurs,
            # avoid blocking install; the pricelist can be created later manually.
            pass

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


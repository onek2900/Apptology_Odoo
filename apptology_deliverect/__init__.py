# -*- coding: utf-8 -*-
from . import controllers
from . import models
from . import wizards
from odoo import api, SUPERUSER_ID


def create_deliverect_payment_method(cr, registry):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})

        # Find all companies
        companies = env['res.company'].search([])

        # Find the bank journal (you might want to make this more flexible)
        bank_journal = env.ref('account.1_bank')

        for company in companies:
            # Check if the payment method already exists for this company
            existing_method = env['pos.payment.method'].search([
                ('name', '=', 'Deliverect'),
                ('company_id', '=', company.id)
            ])

            # Create the payment method if it doesn't exist
            if not existing_method:
                env['pos.payment.method'].create({
                    'name': 'Deliverect',
                    'journal_id': bank_journal.id,
                    'company_id': company.id
                })
# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)



class ResPartner(models.Model):
    """Inherit res.partner to add channel_id field."""
    _inherit = "res.partner"

    channel_id = fields.Char(string='Channel', help='Channel ID the of partner')
    tax_ids = fields.Many2many('account.tax', string='Taxes')

    @api.model_create_multi
    def create(self, vals):
        """Create partner and sync receivable/payable accounts."""
        record = super().create(vals)
        record._sync_customer_accounts()
        return record

    def write(self, vals):
        """Update partner and sync accounts unless skipped via context."""
        if self.env.context.get('skip_account_sync'):
            return super().write(vals)
        res = super().write(vals)
        self._sync_customer_accounts()
        return res

    def _sync_customer_accounts(self):
        """Sync receivable/payable accounts across all companies."""
        for partner in self:
            if partner.property_account_receivable_id:
                partner._sync_account(partner.property_account_receivable_id, 'property_account_receivable_id')
            if partner.property_account_payable_id:
                partner._sync_account(partner.property_account_payable_id, 'property_account_payable_id')

    def _sync_account(self, source_account, field_name):
        """Ensure the account exists in all companies and assign it."""
        companies = self.env['res.company'].sudo().search([])
        for company in companies:
            if company.id == source_account.company_id.id:
                continue

            existing_account = self.env['account.account'].sudo().search([
                ('code', '=', source_account.code),
                ('company_id', '=', company.id)
            ], limit=1)

            if not existing_account:
                try:
                    new_account = self.env['account.account'].sudo().create({
                        'code': source_account.code,
                        'name': source_account.name,
                        'account_type': source_account.account_type,
                        'tax_ids': [(6, 0, source_account.tax_ids.ids)],
                        'allowed_journal_ids': [(6, 0, source_account.allowed_journal_ids.ids)],
                        'tag_ids': [(6, 0, source_account.tag_ids.ids)],
                        'currency_id': source_account.currency_id.id,
                        'group_id': source_account.group_id.id,
                        'reconcile': source_account.reconcile,
                        'company_id': company.id
                    })
                    existing_account = new_account
                    _logger.info(f"Created new account '{source_account.code}' in company {company.name}")
                except Exception as e:
                    _logger.warning(
                        f"Failed to create account '{source_account.code}' in company {company.name}: {str(e)}")
                    continue

            try:
                self.with_company(company).sudo().with_context(skip_account_sync=True).write({
                    field_name: existing_account.id
                })
                _logger.info(
                    f"Assigned account {existing_account.code} to partner '{self.name}' for company {company.name}")
            except Exception as e:
                _logger.warning(
                    f"Failed to assign account to partner '{self.name}' in company {company.name}: {str(e)}")

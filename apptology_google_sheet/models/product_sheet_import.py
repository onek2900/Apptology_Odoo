# -*- coding: utf-8 -*-

from odoo import models, fields, api
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
import logging
import re
import time

_logger = logging.getLogger(__name__)

PRODUCT_TYPES = {
    'Consumable': 'consu',
    'Service': 'service',
    'Storable': 'product',
    'Combo': 'combo'
}

BATCH_SIZE = 1000
MAX_RETRIES = 3
RETRY_DELAY = 2


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    sheet_ext_id = fields.Integer(string="External ID", help="External ID for Product in Google Sheet")
    last_sync_date = fields.Datetime(string="Last Sync Date")

    def get_sheet_credentials(self):
        """Get and validate Google Sheets credentials"""
        try:
            enable_import = self.env['ir.config_parameter'].sudo().get_param(
                'product_gsheet_import.enable_gsheet_import')
            sheet_url = self.env['ir.config_parameter'].sudo().get_param(
                'product_gsheet_import.gsheet_url')
            credentials_str = self.env['ir.config_parameter'].sudo().get_param(
                'product_gsheet_import.gsheet_credentials')

            if not all([enable_import, sheet_url, credentials_str]):
                _logger.warning('Google Sheet import not properly configured')
                return False

            try:
                credentials_dict = json.loads(credentials_str)
                credentials = service_account.Credentials.from_service_account_info(
                    credentials_dict,
                    scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
                )

                pattern = r'/spreadsheets/d/([a-zA-Z0-9-_]+)'
                match = re.search(pattern, sheet_url)
                if not match:
                    _logger.error('Invalid Google Sheet URL format')
                    return False
                return credentials, match.group(1)

            except json.JSONDecodeError:
                _logger.error('Invalid JSON credentials format')
                return False

        except Exception as e:
            _logger.error(f'Error in credentials setup: {str(e)}')
            return False

    def get_data_row_count(self, sheet, sheet_id):
        """Get count of actual data rows (excluding empty rows)"""
        try:
            # Get all values from column A (assuming first column contains sheet_ext_id)
            result = sheet.values().get(
                spreadsheetId=sheet_id,
                range='Sheet1!A:A',
                valueRenderOption='UNFORMATTED_VALUE'
            ).execute()

            values = result.get('values', [])

            # Count rows that have numeric values (sheet_ext_id)
            data_rows = 0
            for row in values[1:]:  # Skip header row
                if row and row[0] and str(row[0]).strip().isdigit():
                    data_rows += 1

            _logger.info(f'Found {data_rows} data rows in sheet')
            return data_rows

        except Exception as e:
            _logger.error(f'Error getting data row count: {str(e)}')
            return 0

    def fetch_batch(self, sheet, sheet_id, start_row, batch_size):
        """Fetch a single batch of data with retry logic"""
        for attempt in range(MAX_RETRIES):
            try:
                range_name = f'Sheet1!A{start_row}:J{start_row + batch_size - 1}'
                result = sheet.values().get(
                    spreadsheetId=sheet_id,
                    range=range_name,
                    valueRenderOption='UNFORMATTED_VALUE'
                ).execute()

                # Filter out empty rows or rows without valid sheet_ext_id
                values = result.get('values', [])
                valid_rows = [
                    row for row in values
                    if row and len(row) >= 5 and str(row[0]).strip().isdigit()
                ]

                return valid_rows

            except Exception as e:
                if attempt < MAX_RETRIES - 1:
                    _logger.warning(f'Retry {attempt + 1}/{MAX_RETRIES} after error: {str(e)}')
                    time.sleep(RETRY_DELAY)
                else:
                    _logger.error(f'Failed to fetch batch after {MAX_RETRIES} attempts')
                    return []

    def create_update_products_batch(self, batch_data):
        """Process a batch of products efficiently"""
        if not batch_data:
            return

        # Prepare category cache
        category_names = {row[9] for row in batch_data if len(row) > 9 and row[9]}
        categories = {cat.name: cat for cat in self.env['pos.category'].search([('name', 'in', list(category_names))])}

        # Prepare existing products cache
        ext_ids = [int(row[0]) for row in batch_data if row[0]]
        existing_products = {
            prod.sheet_ext_id: prod
            for prod in self.search([('sheet_ext_id', 'in', ext_ids)])
        }

        create_vals = []
        update_vals = []

        for row in batch_data:
            try:
                # Get or create category
                category = None
                if len(row) > 9 and row[9]:
                    category_name = str(row[9])
                    if category_name not in categories:
                        categories[category_name] = self.env['pos.category'].create({'name': category_name})
                    category = categories[category_name]

                # Prepare product values
                product_vals = {
                    'sheet_ext_id': int(row[0]),
                    'name': str(row[1]),
                    'detailed_type': PRODUCT_TYPES.get(str(row[2]), 'consu'),
                    'default_code': str(row[3]) if row[3] else False,
                    'barcode': str(row[4]) if row[4] else False,
                    'list_price': float(row[5]) if len(row) > 5 and row[5] else 0.0,
                    'standard_price': float(row[6]) if len(row) > 6 and row[6] else 0.0,
                    'weight': float(row[7]) if len(row) > 7 and row[7] else 0.0,
                    'description_sale': str(row[8]) if len(row) > 8 and row[8] else False,
                    'available_in_pos': True,
                    'pos_categ_ids': [(6, 0, [category.id])] if category else False,
                    'last_sync_date': fields.Datetime.now()
                }

                if product_vals['sheet_ext_id'] in existing_products:
                    update_vals.append((existing_products[product_vals['sheet_ext_id']].id, product_vals))
                else:
                    create_vals.append(product_vals)

            except Exception as e:
                _logger.error(f"Error processing row {row}: {str(e)}")
                continue

        # Bulk create new products
        if create_vals:
            self.create(create_vals)
            _logger.info(f"Created {len(create_vals)} new products")

        # Bulk update existing products
        for product_id, vals in update_vals:
            self.browse(product_id).write(vals)
        _logger.info(f"Updated {len(update_vals)} existing products")

    @api.model
    def _scheduled_import(self):
        """Scheduled method for importing products"""
        if not self.env['ir.config_parameter'].sudo().get_param('product_gsheet_import.enable_gsheet_import'):
            return

        credentials_data = self.get_sheet_credentials()
        if not credentials_data:
            return

        credentials, sheet_id = credentials_data
        service = build('sheets', 'v4', credentials=credentials)
        sheet = service.spreadsheets()

        # Get total data rows
        total_rows = self.get_data_row_count(sheet, sheet_id)
        if not total_rows:
            _logger.error('No valid data rows found in sheet')
            return

        _logger.info(f'Starting import of {total_rows} valid data rows')
        processed_rows = 0
        start_row = 2  # Skip header row

        while processed_rows < total_rows:
            try:
                # Fetch and validate batch
                batch_data = self.fetch_batch(sheet, sheet_id, start_row, BATCH_SIZE)
                if not batch_data:
                    _logger.info('No more valid data rows to process')
                    break

                # Process batch
                self.env.cr.execute('SAVEPOINT product_batch')
                self.create_update_products_batch(batch_data)
                self.env.cr.execute('RELEASE SAVEPOINT product_batch')

                batch_size = len(batch_data)
                processed_rows += batch_size
                start_row += BATCH_SIZE  # Always increment by BATCH_SIZE to maintain proper row counting

                _logger.info(f'Processed {processed_rows}/{total_rows} valid rows')

                # Commit transaction and clear caches periodically
                self.env.cr.commit()
                self.env.clear()

                # Add small delay to avoid API rate limits
                time.sleep(0.5)

            except Exception as e:
                self.env.cr.execute('ROLLBACK TO SAVEPOINT product_batch')
                _logger.error(f'Error processing batch: {str(e)}')
                break

        _logger.info(f'Import completed. Total valid rows processed: {processed_rows}')

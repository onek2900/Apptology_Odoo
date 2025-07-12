from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import UserError
from datetime import datetime,timedelta


class UpdateTaxGrid(models.TransientModel):
    """ Update Tax Grid"""
    _name = "update.tax.grid"
    _description = "Update tax grid"

    date_from = fields.Date(string='Start Date', default=date.today(), required=True)
    date_to = fields.Date(string='End Date', default=date.today(), required=True)
    company_id = fields.Many2one('res.company', string='Company Name', required=True)

    def update_tax_grid(self):
        move_lines = self.env['account.move.line'].search([('date', '>=', self.date_from),
                                                           ('date', '<=', self.date_to),
                                                           ('company_id', '=', self.company_id.id),
                                                           ('move_id.move_type', 'in',
                                                            ['in_invoice', 'out_invoice', 'in_refund', 'out_refund'])])
        not_include_lines = move_lines.filtered(lambda l: l.tax_ids is False and l.tax_repartition_line_id is False)

        for line in move_lines - not_include_lines:
            if line.tax_ids:
                if line.move_id.move_type in ('in_invoice', 'out_invoice'):
                    invoice_repartition_lines = line.tax_ids.mapped('invoice_repartition_line_ids') \
                        .filtered(lambda re_line: re_line.repartition_type == 'base')
                    line.tax_tag_ids = [(6, 0, invoice_repartition_lines.mapped('tag_ids').ids)]

                if line.move_id.move_type in ('in_refund', 'out_refund'):
                    refund_repartition_lines = line.tax_ids.mapped('refund_repartition_line_ids') \
                        .filtered(lambda re_line: re_line.repartition_type == 'base')
                    line.tax_tag_ids = [(6, 0, refund_repartition_lines.mapped('tag_ids').ids)]
            if line.tax_repartition_line_id:
                line.tax_tag_ids = [(6, 0, line.tax_repartition_line_id.mapped('tag_ids').ids)]


from odoo import models, api, _
from odoo.exceptions import UserError
from datetime import datetime,timedelta


class KSA_VAT_REPORT(models.AbstractModel):
    _name = 'report.ksa_vat_report.ksa_vat_report_template'
    _description = 'KSA VAT Report'



    # 1.Standard rated sales invoice amount
    def _get_report_line(self, data):
        cr = self.env.cr
        move_line = self.env['account.move.line']
        company_id = []
        company_id = data['form']['company_id']
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        sale_base = self.env.ref('ksa_vat_report.standard_rated_sales_distribution_invoice_base_tag').id

        sql = """SELECT coalesce((SUM(aml.balance)*-1), 0.00) as standard_rate_invoice_amount FROM account_move_line as aml \
                    INNER JOIN account_move am on (aml.move_id=am.id) \
                    LEFT JOIN account_account_tag_account_move_line_rel as account_tag_rel \
                    ON aml.id = account_tag_rel.account_move_line_id \
                    WHERE am.state='posted' AND aml.company_id = '""" + str(company_id[0]) + """' AND aml.date BETWEEN '""" + str(
            date_from) + """' and '""" + str(date_to) + """' \
                    AND account_tag_rel.account_account_tag_id ='""" + str(sale_base) + """' """

        cr.execute(sql)
        report_line_res = []
        report_line_res = cr.dictfetchall()
        return report_line_res

    # 1.1.Standard rated sales credit note amount
    def _get_report_credit_note_line(self, data):
        cr = self.env.cr
        move_line = self.env['account.move.line']
        company_id = []
        company_id = data['form']['company_id']
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        sale_base_credit_note = self.env.ref('ksa_vat_report.standard_rated_sales_distribution_credit_note_base_tag').id

        sql="""SELECT coalesce((SUM(aml.balance)), 0.00) as standard_rate_credit_amount  FROM account_move_line as aml \
            INNER JOIN account_move am on (aml.move_id=am.id) \
            LEFT JOIN account_account_tag_account_move_line_rel as account_tag_rel \
            ON aml.id = account_tag_rel.account_move_line_id \
            WHERE am.state='posted' AND  aml.company_id = '""" + str(company_id[0]) + """' AND aml.date BETWEEN '""" + str(date_from) + """' and '""" + str(date_to) + """' \
            AND account_tag_rel.account_account_tag_id = '"""+str(sale_base_credit_note)+"""' """

        cr.execute(sql)
        report_line_res = []
        report_line_res = cr.dictfetchall()
        return report_line_res

    # 1.2.Standard rated sales for invoice and credit note vat amount
    def _get_report_vat_line(self, data):
        cr = self.env.cr
        move_line = self.env['account.move.line']
        company_id = []
        company_id = data['form']['company_id']
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        sale_base_vat = self.env.ref('ksa_vat_report.standard_rated_sales_distribution_invoice_base_tax_tag').id
        sale_base_credit_note_vat = self.env.ref(
            'ksa_vat_report.standard_rated_sales_distribution_credit_note_base_tax_tag').id

        sql = """SELECT coalesce((SUM(aml.balance)*-1), 0.00) as standard_rate_vat_amount  FROM account_move_line as aml \
                  INNER JOIN account_move am on (aml.move_id=am.id) \
                  LEFT JOIN account_account_tag_account_move_line_rel as account_tag_rel \
                  ON aml.id = account_tag_rel.account_move_line_id \
                  WHERE am.state='posted' AND  aml.company_id = '""" + str(company_id[0]) + """' AND (aml.date BETWEEN '""" + str(
            date_from) + """' and '""" + str(date_to) + """') \
                  AND (account_tag_rel.account_account_tag_id = '""" + str(sale_base_vat) + """' OR account_tag_rel.account_account_tag_id = '""" + str(sale_base_credit_note_vat) + """') """


        cr.execute(sql)
        # report_line_res = []
        report_line_res = cr.dictfetchall()
        return report_line_res



    # 2. Zero Rated Domestic Sales invoice amount
    def _get_report_zero_rated_line(self, data):
        cr = self.env.cr
        move_line = self.env['account.move.line']
        company_id = []
        company_id = data['form']['company_id']
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        sale_base = self.env.ref('ksa_vat_report.zero_rated_distribution_invoice_base_tag').id

        sql = """SELECT coalesce((SUM(aml.balance)*-1), 0.00) as zero_rate_invoice_amount FROM account_move_line as aml \
                    INNER JOIN account_move am on (aml.move_id=am.id) \
                    LEFT JOIN account_account_tag_account_move_line_rel as account_tag_rel \
                    ON aml.id = account_tag_rel.account_move_line_id \
                    WHERE am.state='posted' AND aml.company_id = '""" + str(company_id[0]) + """' AND aml.date BETWEEN '""" + str(
            date_from) + """' and '""" + str(date_to) + """' \
                    AND account_tag_rel.account_account_tag_id ='""" + str(sale_base) + """' """

        cr.execute(sql)
        report_line_res = []
        report_line_res = cr.dictfetchall()
        return report_line_res

    # 2.1 Zero Rated Domestic Sales credit note amount
    def _get_report_zero_rated_credit_note_line(self, data):
        cr = self.env.cr
        move_line = self.env['account.move.line']
        company_id = []
        company_id = data['form']['company_id']
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        sale_base_credit_note = self.env.ref('ksa_vat_report.zero_rated_distribution_credit_note_base_tag').id

        sql="""SELECT coalesce((SUM(aml.balance)), 0.00) as zero_rate_credit_amount  FROM account_move_line as aml \
            INNER JOIN account_move am on (aml.move_id=am.id) \
            LEFT JOIN account_account_tag_account_move_line_rel as account_tag_rel \
            ON aml.id = account_tag_rel.account_move_line_id \
            WHERE am.state='posted' AND  aml.company_id = '""" + str(company_id[0]) + """' AND aml.date BETWEEN '""" + str(date_from) + """' and '""" + str(date_to) + """' \
            AND account_tag_rel.account_account_tag_id = '"""+str(sale_base_credit_note)+"""' """

        cr.execute(sql)
        report_line_res = []
        report_line_res = cr.dictfetchall()
        return report_line_res

        # 3. Exports  Sales



    # 3. Export Sales for invoice amount
    def _get_report_export_sale_line(self, data):
        cr = self.env.cr
        move_line = self.env['account.move.line']
        company_id = []
        company_id = data['form']['company_id']
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        sale_base = self.env.ref('ksa_vat_report.exports_sales_distribution_invoice_base_tag').id

        sql = """SELECT coalesce((SUM(aml.balance)*-1), 0.00) as export_rate_invoice_amount FROM account_move_line as aml \
                       INNER JOIN account_move am on (aml.move_id=am.id) \
                       LEFT JOIN account_account_tag_account_move_line_rel as account_tag_rel \
                       ON aml.id = account_tag_rel.account_move_line_id \
                       WHERE am.state='posted' AND aml.company_id = '""" + str(
            company_id[0]) + """' AND aml.date BETWEEN '""" + str(
            date_from) + """' and '""" + str(date_to) + """' \
                       AND account_tag_rel.account_account_tag_id ='""" + str(sale_base) + """' """

        cr.execute(sql)
        report_line_res = []
        report_line_res = cr.dictfetchall()
        return report_line_res

    # 3.1 Export Sales for credit note amount
    def _get_report_export_sale_credit_note_line(self, data):
        cr = self.env.cr
        move_line = self.env['account.move.line']
        company_id = []
        company_id = data['form']['company_id']
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        sale_base_credit_note = self.env.ref('ksa_vat_report.exports_sales_distribution_credit_note_base_tag').id

        sql = """SELECT coalesce((SUM(aml.balance)), 0.00) as export_rate_credit_amount  FROM account_move_line as aml \
               INNER JOIN account_move am on (aml.move_id=am.id) \
               LEFT JOIN account_account_tag_account_move_line_rel as account_tag_rel \
               ON aml.id = account_tag_rel.account_move_line_id \
               WHERE am.state='posted' AND  aml.company_id = '""" + str(
            company_id[0]) + """' AND aml.date BETWEEN '""" + str(date_from) + """' and '""" + str(date_to) + """' \
               AND account_tag_rel.account_account_tag_id = '""" + str(sale_base_credit_note) + """' """

        cr.execute(sql)
        report_line_res = []
        report_line_res = cr.dictfetchall()
        return report_line_res

        # 3. Exempt  Sales

    # 4. Exempt Sales for invoice amount
    def _get_report_exempt_sale_line(self, data):
        cr = self.env.cr
        move_line = self.env['account.move.line']
        company_id = []
        company_id = data['form']['company_id']
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        sale_base = self.env.ref('ksa_vat_report.exempt_sales_distribution_invoice_base_tag').id

        sql = """SELECT coalesce((SUM(aml.balance)*-1), 0.00) as exempt_rate_invoice_amount FROM account_move_line as aml \
                       INNER JOIN account_move am on (aml.move_id=am.id) \
                       LEFT JOIN account_account_tag_account_move_line_rel as account_tag_rel \
                       ON aml.id = account_tag_rel.account_move_line_id \
                       WHERE am.state='posted' AND aml.company_id = '""" + str(
            company_id[0]) + """' AND aml.date BETWEEN '""" + str(
            date_from) + """' and '""" + str(date_to) + """' \
                       AND account_tag_rel.account_account_tag_id ='""" + str(sale_base) + """' """

        cr.execute(sql)
        report_line_res = []
        report_line_res = cr.dictfetchall()
        return report_line_res

    # 4.1 Exempt Sales for credit note amount
    def _get_report_exempt_sale_credit_note_line(self, data):
        cr = self.env.cr
        move_line = self.env['account.move.line']
        company_id = []
        company_id = data['form']['company_id']
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        sale_base_credit_note = self.env.ref('ksa_vat_report.exempt_sales_distribution_credit_note_base_tag').id

        sql = """SELECT coalesce((SUM(aml.balance)), 0.00) as exempt_rate_credit_amount  FROM account_move_line as aml \
               INNER JOIN account_move am on (aml.move_id=am.id) \
               LEFT JOIN account_account_tag_account_move_line_rel as account_tag_rel \
               ON aml.id = account_tag_rel.account_move_line_id \
               WHERE am.state='posted' AND  aml.company_id = '""" + str(
            company_id[0]) + """' AND aml.date BETWEEN '""" + str(date_from) + """' and '""" + str(date_to) + """' \
               AND account_tag_rel.account_account_tag_id = '""" + str(sale_base_credit_note) + """' """

        cr.execute(sql)
        report_line_res = []
        report_line_res = cr.dictfetchall()
        return report_line_res



    # 5. Standard rated Purchases for invoice amount
    def _get_standard_purchases_report_line(self, data):
        cr = self.env.cr
        move_line = self.env['account.move.line']
        company_id = []
        company_id = data['form']['company_id']
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        sale_base = self.env.ref('ksa_vat_report.standard_rated_domestic_purchases_base_tag').id

        sql = """SELECT coalesce((SUM(aml.balance)), 0.00) as standard_rate_purchase_amount FROM account_move_line as aml \
                                        INNER JOIN account_move am on (aml.move_id=am.id) \
                                        LEFT JOIN account_account_tag_account_move_line_rel as account_tag_rel \
                                        ON aml.id = account_tag_rel.account_move_line_id \
                                        WHERE am.state='posted'  AND aml.company_id = '""" + str(
            company_id[0]) + """' AND aml.date BETWEEN '""" + str(
            date_from) + """' and '""" + str(date_to) + """' \
                                        AND account_tag_rel.account_account_tag_id ='""" + str(sale_base) + """' """

        cr.execute(sql)
        report_line_res = []
        report_line_res = cr.dictfetchall()
        return report_line_res

    # 5.1 Standard rated Purchases for credit note amount
    def _get_standard_purchases_report_credit_note_line(self, data):
        cr = self.env.cr
        move_line = self.env['account.move.line']
        company_id = []
        company_id = data['form']['company_id']
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        sale_base_credit_note = self.env.ref(
            'ksa_vat_report.standard_rated_domestic_purchases_debit_base_tag').id

        sql = """SELECT coalesce((SUM(aml.balance)*-1), 0.00) as standard_rate_purchase_credit_amount  FROM account_move_line as aml \
                       INNER JOIN account_move am on (aml.move_id=am.id) \
                       LEFT JOIN account_account_tag_account_move_line_rel as account_tag_rel \
                       ON aml.id = account_tag_rel.account_move_line_id \
                       WHERE am.state='posted' AND aml.company_id = '""" + str(
            company_id[0]) + """' AND aml.date BETWEEN '""" + str(date_from) + """' and '""" + str(date_to) + """' \
                       AND account_tag_rel.account_account_tag_id = '""" + str(sale_base_credit_note) + """' """

        cr.execute(sql)
        report_line_res = []
        report_line_res = cr.dictfetchall()
        return report_line_res

    # 5.2.Standard rated purchase for invoice and credit note vat amount
    def _get_standard_purchases_report_vat_line(self, data):
        cr = self.env.cr
        move_line = self.env['account.move.line']
        company_id = []
        company_id = data['form']['company_id']
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        purchase_base_vat = self.env.ref('ksa_vat_report.standard_rated_domestic_purchases_vat_base_tag').id
        purchase_base_credit_note_vat = self.env.ref(
            'ksa_vat_report.standard_rated_domestic_purchases_debit_vat_base_tag').id

        sql = """SELECT coalesce((SUM(aml.balance)), 0.00) as standard_rate_purchase_vat_amount  FROM account_move_line as aml \
                              INNER JOIN account_move am on (aml.move_id=am.id) \
                              LEFT JOIN account_account_tag_account_move_line_rel as account_tag_rel \
                              ON aml.id = account_tag_rel.account_move_line_id \
                              WHERE am.state='posted'    AND  aml.company_id = '""" + str(
            company_id[0]) + """' AND (aml.date BETWEEN '""" + str(
            date_from) + """' and '""" + str(date_to) + """') \
                              AND (account_tag_rel.account_account_tag_id = '""" + str(
            purchase_base_vat) + """' OR account_tag_rel.account_account_tag_id = '""" + str(
            purchase_base_credit_note_vat) + """') """

        cr.execute(sql)
        # report_line_res = []
        report_line_res = cr.dictfetchall()
        return report_line_res


    # Imports subject to VAT paid at custom
    # 6. Import VAT Purchases for invoice amount
    def _get_import_purchases_report_line(self, data):
        cr = self.env.cr
        move_line = self.env['account.move.line']
        company_id = []
        company_id = data['form']['company_id']
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        import_purchase_base = self.env.ref('ksa_vat_report.import_purchases_base_tag').id

        sql = """SELECT coalesce((SUM(aml.balance)), 0.00) as import_purchase_amount FROM account_move_line as aml \
                                           INNER JOIN account_move am on (aml.move_id=am.id) \
                                           LEFT JOIN account_account_tag_account_move_line_rel as account_tag_rel \
                                           ON aml.id = account_tag_rel.account_move_line_id \
                                           WHERE am.state='posted'  AND aml.company_id = '""" + str(
            company_id[0]) + """' AND aml.date BETWEEN '""" + str(
            date_from) + """' and '""" + str(date_to) + """' \
                                           AND account_tag_rel.account_account_tag_id ='""" + str(import_purchase_base) + """' """

        cr.execute(sql)
        report_line_res = []
        report_line_res = cr.dictfetchall()
        return report_line_res

    # 6.1 Import VAT Purchases for credit note amount
    def _get_import_purchases_report_credit_note_line(self, data):
        cr = self.env.cr
        move_line = self.env['account.move.line']
        company_id = []
        company_id = data['form']['company_id']
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        import_base_credit_note = self.env.ref(
            'ksa_vat_report.import_purchases_credit_base_tag').id

        sql = """SELECT coalesce((SUM(aml.balance)*-1), 0.00) as import_purchase_credit_amount  FROM account_move_line as aml \
                          INNER JOIN account_move am on (aml.move_id=am.id) \
                          LEFT JOIN account_account_tag_account_move_line_rel as account_tag_rel \
                          ON aml.id = account_tag_rel.account_move_line_id \
                          WHERE am.state='posted' AND aml.company_id = '""" + str(
            company_id[0]) + """' AND aml.date BETWEEN '""" + str(date_from) + """' and '""" + str(date_to) + """' \
                          AND account_tag_rel.account_account_tag_id = '""" + str(import_base_credit_note) + """' """

        cr.execute(sql)
        report_line_res = []
        report_line_res = cr.dictfetchall()
        return report_line_res

    # 6.2.Import VAT Purchases for invoice and credit note vat amount
    def _get_import_purchases_report_vat_line(self, data):
        cr = self.env.cr
        move_line = self.env['account.move.line']
        company_id = []
        company_id = data['form']['company_id']
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        import_base_vat = self.env.ref('ksa_vat_report.import_domestic_purchases_vat_base_tag').id
        import_base_credit_note_vat = self.env.ref(
            'ksa_vat_report.import_domestic_purchases_credit_vat_base_tag').id

        sql = """SELECT coalesce((SUM(aml.balance)), 0.00) as import_purchase_vat_amount  FROM account_move_line as aml \
                                 INNER JOIN account_move am on (aml.move_id=am.id) \
                                 LEFT JOIN account_account_tag_account_move_line_rel as account_tag_rel \
                                 ON aml.id = account_tag_rel.account_move_line_id \
                                 WHERE am.state='posted'    AND  aml.company_id = '""" + str(
            company_id[0]) + """' AND (aml.date BETWEEN '""" + str(
            date_from) + """' and '""" + str(date_to) + """') \
                                 AND (account_tag_rel.account_account_tag_id = '""" + str(
            import_base_vat) + """' OR account_tag_rel.account_account_tag_id = '""" + str(
            import_base_credit_note_vat) + """') """

        cr.execute(sql)
        # report_line_res = []
        report_line_res = cr.dictfetchall()
        return report_line_res

        # 7. Import VAT Purchases Reverse



    #Imports subject to VAT accounted for through reverse charge mechanism
    # 7. Import VAT Purchases reverse for invoice amount
    def _get_import_purchases_reverse_report_line(self, data):
        cr = self.env.cr
        move_line = self.env['account.move.line']
        company_id = []
        company_id = data['form']['company_id']
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        import_purchase_reverse_base = self.env.ref('ksa_vat_report.import_purchases_reverses_base_tag').id

        sql = """SELECT coalesce((SUM(aml.balance)), 0.00) as import_purchase_reverse_amount FROM account_move_line as aml \
                                              INNER JOIN account_move am on (aml.move_id=am.id) \
                                              LEFT JOIN account_account_tag_account_move_line_rel as account_tag_rel \
                                              ON aml.id = account_tag_rel.account_move_line_id \
                                              WHERE am.state='posted'  AND aml.company_id = '""" + str(
            company_id[0]) + """' AND aml.date BETWEEN '""" + str(
            date_from) + """' and '""" + str(date_to) + """' \
                                              AND account_tag_rel.account_account_tag_id ='""" + str(
            import_purchase_reverse_base) + """' """

        cr.execute(sql)
        report_line_res = []
        report_line_res = cr.dictfetchall()
        return report_line_res

    # 7.1 Import VAT Purchases reverse for credit note amount
    def _get_import_purchases_reverse_report_credit_note_line(self, data):
        cr = self.env.cr
        move_line = self.env['account.move.line']
        company_id = []
        company_id = data['form']['company_id']
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        import_base_credit_note_reverse = self.env.ref(
            'ksa_vat_report.import_purchases_credit_reverses_base_tag').id

        sql = """SELECT coalesce((SUM(aml.balance)*-1), 0.00) as import_purchase_reverse_credit_amount  FROM account_move_line as aml \
                             INNER JOIN account_move am on (aml.move_id=am.id) \
                             LEFT JOIN account_account_tag_account_move_line_rel as account_tag_rel \
                             ON aml.id = account_tag_rel.account_move_line_id \
                             WHERE am.state='posted' AND aml.company_id = '""" + str(
            company_id[0]) + """' AND aml.date BETWEEN '""" + str(date_from) + """' and '""" + str(date_to) + """' \
                             AND account_tag_rel.account_account_tag_id = '""" + str(import_base_credit_note_reverse) + """' """

        cr.execute(sql)
        report_line_res = []
        report_line_res = cr.dictfetchall()
        return report_line_res

    # 7.2 Import VAT Purchases reverse for invoice and credit note vat amount
    def _get_import_purchases_reverse_report_vat_line(self, data):
        cr = self.env.cr
        move_line = self.env['account.move.line']
        company_id = []
        company_id = data['form']['company_id']
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        import_base_vat_reverse = self.env.ref('ksa_vat_report.import_domestic_purchases_vat_reverses_base_tag').id
        import_base_credit_note_vat_reverse = self.env.ref(
            'ksa_vat_report.import_domestic_purchases_credit_vat_reverses_base_tag').id

        sql = """SELECT coalesce((SUM(aml.balance)), 0.00) as import_purchase_reverse_vat_amount  FROM account_move_line as aml \
                                    INNER JOIN account_move am on (aml.move_id=am.id) \
                                    LEFT JOIN account_account_tag_account_move_line_rel as account_tag_rel \
                                    ON aml.id = account_tag_rel.account_move_line_id \
                                    WHERE am.state='posted'    AND  aml.company_id = '""" + str(
            company_id[0]) + """' AND (aml.date BETWEEN '""" + str(
            date_from) + """' and '""" + str(date_to) + """') \
                                    AND (account_tag_rel.account_account_tag_id = '""" + str(
            import_base_vat_reverse) + """' OR account_tag_rel.account_account_tag_id = '""" + str(
            import_base_credit_note_vat_reverse) + """') """

        cr.execute(sql)
        # report_line_res = []
        report_line_res = cr.dictfetchall()
        return report_line_res



    # 8. Zero Rated Purchases  for invoice amount
    def _get_purchase_report_zero_rated_line(self, data):
        cr = self.env.cr
        move_line = self.env['account.move.line']
        company_id = []
        company_id = data['form']['company_id']
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        sale_base = self.env.ref('ksa_vat_report.zero_rated_distribution_purchases_base_tag').id

        sql = """SELECT coalesce((SUM(aml.balance)), 0.00) as zero_rate_purchase_amount FROM account_move_line as aml \
                                INNER JOIN account_move am on (aml.move_id=am.id) \
                                LEFT JOIN account_account_tag_account_move_line_rel as account_tag_rel \
                                ON aml.id = account_tag_rel.account_move_line_id \
                                WHERE am.state='posted' AND aml.company_id = '""" + str(
            company_id[0]) + """' AND aml.date BETWEEN '""" + str(
            date_from) + """' and '""" + str(date_to) + """' \
                                AND account_tag_rel.account_account_tag_id ='""" + str(sale_base) + """' """

        cr.execute(sql)
        report_line_res = []
        report_line_res = cr.dictfetchall()
        return report_line_res

    # 8.1 Zero Rated Purchases  for credit note amount
    def _get_purchases_report_zero_rated_credit_note_line(self, data):
        cr = self.env.cr
        move_line = self.env['account.move.line']
        company_id = []
        company_id = data['form']['company_id']
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        sale_base_credit_note = self.env.ref('ksa_vat_report.zero_rated_distribution_debit_note_base_tag').id

        sql = """SELECT coalesce((SUM(aml.balance)*-1), 0.00) as zero_rate_purchase_credit_amount  FROM account_move_line as aml \
                            INNER JOIN account_move am on (aml.move_id=am.id) \
                            LEFT JOIN account_account_tag_account_move_line_rel as account_tag_rel \
                            ON aml.id = account_tag_rel.account_move_line_id \
                            WHERE am.state='posted' AND  aml.company_id = '""" + str(
            company_id[0]) + """' AND aml.date BETWEEN '""" + str(date_from) + """' and '""" + str(date_to) + """' \
                            AND account_tag_rel.account_account_tag_id = '""" + str(sale_base_credit_note) + """' """

        cr.execute(sql)
        report_line_res = []
        report_line_res = cr.dictfetchall()
        return report_line_res



    # 9. Exempt Purchases for invoice amount
    def _get_report_exempt_purchase_line(self, data):
        cr = self.env.cr
        move_line = self.env['account.move.line']
        company_id = []
        company_id = data['form']['company_id']
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        sale_base = self.env.ref('ksa_vat_report.exempt_purchases_distribution_invoice_base_tag').id

        sql = """SELECT coalesce((SUM(aml.balance)), 0.00) as exempt_rate_purchase_amount FROM account_move_line as aml \
                                   INNER JOIN account_move am on (aml.move_id=am.id) \
                                   LEFT JOIN account_account_tag_account_move_line_rel as account_tag_rel \
                                   ON aml.id = account_tag_rel.account_move_line_id \
                                   WHERE am.state='posted' AND aml.company_id = '""" + str(
            company_id[0]) + """' AND aml.date BETWEEN '""" + str(
            date_from) + """' and '""" + str(date_to) + """' \
                                   AND account_tag_rel.account_account_tag_id ='""" + str(sale_base) + """' """

        cr.execute(sql)
        report_line_res = []
        report_line_res = cr.dictfetchall()
        return report_line_res

    # 9.1 Exempt Purchases for credit note amount
    def _get_report_exempt_purchase_credit_note_line(self, data):
        cr = self.env.cr
        move_line = self.env['account.move.line']
        company_id = []
        company_id = data['form']['company_id']
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        sale_base_credit_note = self.env.ref('ksa_vat_report.exempt_purchases_distribution_debit_note_base_tag').id

        sql = """SELECT coalesce((SUM(aml.balance)*-1), 0.00) as exempt_rate_purchase_credit_amount  FROM account_move_line as aml \
                           INNER JOIN account_move am on (aml.move_id=am.id) \
                           LEFT JOIN account_account_tag_account_move_line_rel as account_tag_rel \
                           ON aml.id = account_tag_rel.account_move_line_id \
                           WHERE am.state='posted' AND  aml.company_id = '""" + str(
            company_id[0]) + """' AND aml.date BETWEEN '""" + str(date_from) + """' and '""" + str(date_to) + """' \
                           AND account_tag_rel.account_account_tag_id = '""" + str(sale_base_credit_note) + """' """

        cr.execute(sql)
        report_line_res = []
        report_line_res = cr.dictfetchall()
        return report_line_res


    # 10. VAT credit carried forward from previous period for sales
    def _get_VAT_credit_carried_forward_from_previous_period_line_for_sale(self, data):
        cr = self.env.cr
        move_line = self.env['account.move.line']
        company_id = []
        company_id = data['form']['company_id']
        date_from = data['form']['date_from']
        date_from_date = datetime.strptime(date_from,'%Y-%m-%d')

        previous_date = date_from_date -timedelta(days=1)
        vat_report_previous_start_date = (self.env['ir.config_parameter'].sudo().get_param(
            "ksa_vat_report.vat_report_previous_start_date"))
        date_to = data['form']['date_to']
        sale_base_vat = self.env.ref('ksa_vat_report.standard_rated_sales_distribution_invoice_base_tax_tag').id
        sale_base_credit_note_vat = self.env.ref(
            'ksa_vat_report.standard_rated_sales_distribution_credit_note_base_tax_tag').id

        sql = """SELECT coalesce((SUM(aml.balance)*-1), 0.00) as vat_amount_previous_sale  FROM account_move_line as aml \
                         INNER JOIN account_move am on (aml.move_id=am.id) \
                         LEFT JOIN account_account_tag_account_move_line_rel as account_tag_rel \
                         ON aml.id = account_tag_rel.account_move_line_id \
                         WHERE am.state='posted' AND  aml.company_id = '""" + str(
            company_id[0]) + """' AND (aml.date BETWEEN '""" + str(
            vat_report_previous_start_date) + """' and '""" + str(previous_date) + """') \
                         AND (account_tag_rel.account_account_tag_id = '""" + str(
            sale_base_vat) + """' OR account_tag_rel.account_account_tag_id = '""" + str(
            sale_base_credit_note_vat) + """') """

        cr.execute(sql)
        report_line_res = []
        report_line_res = cr.dictfetchall()
        return report_line_res

    # 10.1 VAT credit carried forward from previous period for purchase
    def _get_VAT_credit_carried_forward_from_previous_period_line_for_purchase(self, data):
        cr = self.env.cr
        move_line = self.env['account.move.line']
        company_id = []
        company_id = data['form']['company_id']
        date_from = data['form']['date_from']
        date_from_date = datetime.strptime(date_from, '%Y-%m-%d')
        previous_date = date_from_date - timedelta(days=1)

        vat_report_previous_start_date = (self.env['ir.config_parameter'].sudo().get_param(
            "ksa_vat_report.vat_report_previous_start_date"))
        date_to = data['form']['date_to']

        purchase_base_vat = self.env.ref('ksa_vat_report.standard_rated_domestic_purchases_vat_base_tag').id
        purchase_base_credit_note_vat = self.env.ref(
            'ksa_vat_report.standard_rated_domestic_purchases_debit_vat_base_tag').id
        import_base_vat = self.env.ref('ksa_vat_report.import_domestic_purchases_vat_base_tag').id
        import_base_credit_note_vat = self.env.ref(
            'ksa_vat_report.import_domestic_purchases_credit_vat_base_tag').id
        import_base_vat_reverse = self.env.ref('ksa_vat_report.import_domestic_purchases_vat_reverses_base_tag').id
        import_base_credit_note_vat_reverse = self.env.ref(
            'ksa_vat_report.import_domestic_purchases_credit_vat_reverses_base_tag').id

        sql = """SELECT coalesce((SUM(aml.balance)), 0.00) as vat_amount_previous_purchase  FROM account_move_line as aml \
                                      INNER JOIN account_move am on (aml.move_id=am.id) \
                                      LEFT JOIN account_account_tag_account_move_line_rel as account_tag_rel \
                                      ON aml.id = account_tag_rel.account_move_line_id \
                                      WHERE am.state='posted'    AND  aml.company_id = '""" + str(
            company_id[0]) + """' AND (aml.date BETWEEN '""" + str(
            vat_report_previous_start_date) + """' and '""" + str(previous_date) + """') \
                                      AND (account_tag_rel.account_account_tag_id = '""" + str(
            purchase_base_vat) + """' OR account_tag_rel.account_account_tag_id = '""" + str(
            purchase_base_credit_note_vat) + """' OR account_tag_rel.account_account_tag_id = '""" + str(
            import_base_vat) + """' OR account_tag_rel.account_account_tag_id = '""" + str(
            import_base_credit_note_vat) + """' OR account_tag_rel.account_account_tag_id = '""" + str(
            import_base_vat_reverse) + """' OR account_tag_rel.account_account_tag_id = '""" + str(
            import_base_credit_note_vat_reverse) + """') """

        cr.execute(sql)
        report_line_res = []
        report_line_res = cr.dictfetchall()
        return report_line_res





    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form') or not self.env.context.get('active_model'):
            raise UserError(
                _("Form content is missing, this report cannot be printed."))

        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_ids', []))

        # SALES
        get_report_lines = self._get_report_line(data)
        get_report_credit_note_lines = self._get_report_credit_note_line(data)
        get_report_vat_lines = self._get_report_vat_line(data)

        get_report_zero_rated_lines = self._get_report_zero_rated_line(data)
        get_report_zero_rated_credit_note_lines = self._get_report_zero_rated_credit_note_line(data)

        get_report_export_sale_lines = self._get_report_export_sale_line(data)
        get_report_export_sale_credit_note_lines = self._get_report_export_sale_credit_note_line(data)

        get_report_exempt_sale_lines = self._get_report_exempt_sale_line(data)
        get_report_exempt_sale_credit_note_lines = self._get_report_exempt_sale_credit_note_line(data)

        # TOTAL SALE
        total_sale = get_report_lines[0].get('standard_rate_invoice_amount') + get_report_zero_rated_lines[0].get(
            'zero_rate_invoice_amount') + get_report_export_sale_lines[0].get('export_rate_invoice_amount') + \
                     get_report_exempt_sale_lines[0].get('exempt_rate_invoice_amount')
        total_credit = get_report_credit_note_lines[0].get('standard_rate_credit_amount') + \
                       get_report_zero_rated_credit_note_lines[0].get('zero_rate_credit_amount') + \
                       get_report_export_sale_credit_note_lines[0].get('export_rate_credit_amount') + \
                       get_report_exempt_sale_credit_note_lines[0].get('exempt_rate_credit_amount')
        total_sale_vat = get_report_vat_lines[0].get('standard_rate_vat_amount')


        # PURCHASES
        get_standard_purchases_report_lines = self._get_standard_purchases_report_line(data)
        get_standard_purchases_report_credit_note_lines = self._get_standard_purchases_report_credit_note_line(data)
        get_standard_purchases_report_vat_lines = self._get_standard_purchases_report_vat_line(data)

        get_import_purchases_report_lines = self._get_import_purchases_report_line(data)
        get_import_purchases_report_credit_note_lines = self._get_import_purchases_report_credit_note_line(data)
        get_import_purchases_report_vat_lines = self._get_import_purchases_report_vat_line(data)

        get_import_purchases_reverse_report_lines = self._get_import_purchases_reverse_report_line(data)
        get_import_purchases_reverse_report_credit_note_lines = self._get_import_purchases_reverse_report_credit_note_line(data)
        get_import_purchases_reverse_report_vat_lines = self._get_import_purchases_reverse_report_vat_line(data)

        get_purchase_report_zero_rated_lines = self._get_purchase_report_zero_rated_line(data)
        get_purchases_report_zero_rated_credit_note_lines = self._get_purchases_report_zero_rated_credit_note_line(data)

        get_report_exempt_purchase_lines = self._get_report_exempt_purchase_line(data)
        get_report_exempt_purchase_credit_note_lines = self._get_report_exempt_purchase_credit_note_line(data)

        # TOTAL PURCHASE
        total_purchase = get_standard_purchases_report_lines[0].get('standard_rate_purchase_amount') + \
                         get_purchase_report_zero_rated_lines[0].get('zero_rate_purchase_amount') + \
                         get_report_exempt_purchase_lines[0].get('exempt_rate_purchase_amount') + \
                         get_import_purchases_report_lines[0].get('import_purchase_amount') + \
                         get_import_purchases_reverse_report_lines[0].get('import_purchase_reverse_amount')
        total_purchase_credit = get_standard_purchases_report_credit_note_lines[0].get('standard_rate_purchase_credit_amount') + \
                         get_purchases_report_zero_rated_credit_note_lines[0].get('zero_rate_purchase_credit_amount') + \
                         get_report_exempt_purchase_credit_note_lines[0].get('exempt_rate_purchase_credit_amount') + \
                         get_import_purchases_report_credit_note_lines[0].get('import_purchase_credit_amount') + \
                         get_import_purchases_reverse_report_credit_note_lines[0].get('import_purchase_reverse_credit_amount')

        total_purchase_vat = get_standard_purchases_report_vat_lines[0].get('standard_rate_purchase_vat_amount') + \
                             get_import_purchases_report_vat_lines[0].get('import_purchase_vat_amount') + \
                             get_import_purchases_reverse_report_vat_lines[0].get('import_purchase_reverse_vat_amount')

        total_vat_due_for_current_period=total_sale_vat-total_purchase_vat

        # VAT credit carried forward from previous period
        get_VAT_credit_carried_forward_from_previous_period_line_for_sales = self._get_VAT_credit_carried_forward_from_previous_period_line_for_sale(data)
        get_VAT_credit_carried_forward_from_previous_period_line_for_purchase = self._get_VAT_credit_carried_forward_from_previous_period_line_for_purchase(data)

        previous_period_vat_amount=get_VAT_credit_carried_forward_from_previous_period_line_for_sales[0].get('vat_amount_previous_sale')-get_VAT_credit_carried_forward_from_previous_period_line_for_purchase[0].get('vat_amount_previous_purchase')
        previous_period_vat = previous_period_vat_amount if previous_period_vat_amount and previous_period_vat_amount<0 else 0
        # NET VAT AMOUNT
        net_vat_due=total_vat_due_for_current_period+previous_period_vat






        return {
            'doc_ids': docids,
            'doc_model': model,
            'data': data['form'],
            'docs': docs,
            'get_report_line': get_report_lines[0],
            'get_report_credit_note_line':get_report_credit_note_lines[0],
            'get_report_vat_line':get_report_vat_lines[0],
            'get_report_zero_rated_line':get_report_zero_rated_lines[0],
            'get_report_zero_rated_credit_note_line':get_report_zero_rated_credit_note_lines[0],
            'get_report_export_sale_line':get_report_export_sale_lines[0],
            'get_report_export_sale_credit_note_line':get_report_export_sale_credit_note_lines[0],
            'get_report_exempt_sale_line':get_report_exempt_sale_lines[0],
            'get_report_exempt_sale_credit_note_line':get_report_exempt_sale_credit_note_lines[0],
            'total_sale':total_sale,
            'total_credit': total_credit,
            'total_vat': total_sale_vat,
            'get_standard_purchases_report_line': get_standard_purchases_report_lines[0],
            'get_standard_purchases_report_credit_note_line': get_standard_purchases_report_credit_note_lines[0],
            'get_standard_purchases_report_vat_line': get_standard_purchases_report_vat_lines[0],
            'get_import_purchases_report_line': get_import_purchases_report_lines[0],
            'get_import_purchases_report_credit_note_line': get_import_purchases_report_credit_note_lines[0],
            'get_import_purchases_report_vat_line': get_import_purchases_report_vat_lines[0],
            'get_import_purchases_reverse_report_line': get_import_purchases_reverse_report_lines[0],
            'get_import_purchases_reverse_report_credit_note_line':get_import_purchases_reverse_report_credit_note_lines[0],
            'get_import_purchases_reverse_report_vat_line': get_import_purchases_reverse_report_vat_lines[0],
            'get_purchase_report_zero_rated_line': get_purchase_report_zero_rated_lines[0],
            'get_purchases_report_zero_rated_credit_note_line': get_purchases_report_zero_rated_credit_note_lines[0],
            'get_report_exempt_purchase_line': get_report_exempt_purchase_lines[0],
            'get_report_exempt_purchase_credit_note_line': get_report_exempt_purchase_credit_note_lines[0],
            'total_purchase':total_purchase,
            'total_purchase_credit':total_purchase_credit,
            'total_purchase_vat':total_purchase_vat,
            'total_vat_due_for_current_period':total_vat_due_for_current_period,
            'previous_period_vat':previous_period_vat,
            'net_vat_due':net_vat_due

        }








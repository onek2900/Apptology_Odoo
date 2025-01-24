from odoo import models


class MailMail(models.AbstractModel):
    _inherit = "mail.mail"

    def _prepare_outgoing_body(self):
        body_html = super()._prepare_outgoing_body()
        return self.env["mail.render.mixin"].replace_branding(
            body_html or "", to_keep=self.body
        )
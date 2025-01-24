
import re

from lxml import etree, html
from markupsafe import Markup

from odoo import api, models


class MailRenderMixin(models.AbstractModel):
    _inherit = "mail.render.mixin"

    def replace_branding(self, value, to_keep=None):
        if len(value) < 20:
            return value

        # value can be bytes or markup; ensure we get a proper string and preserve type
        back_to_bytes = False
        back_to_markup = False
        if isinstance(value, bytes):
            back_to_bytes = True
            value = value.decode()
        if isinstance(value, Markup):
            back_to_markup = True

        has_dev_odoo_link = re.search(
            r"<a\s(.*)dev\.odoo\.com", value, flags=re.IGNORECASE
        )
        has_odoo_link = re.search(r"<a\s(.*)odoo\.com", value, flags=re.IGNORECASE)

        if has_odoo_link and not has_dev_odoo_link:
            # Preserve explicit message body content
            if to_keep:
                value = value.replace(to_keep, "<body_msg></body_msg>")

            tree = html.fromstring(value)

            # Replace Odoo references with Apptology
            odoo_anchors = tree.xpath('//a[contains(@href,"odoo.com")]')
            for elem in odoo_anchors:
                parent = elem.getparent()
                # Create new Apptology anchor
                new_anchor = etree.Element('a')
                new_anchor.text = 'Apptology'
                new_anchor.set('href', 'https://www.apptology.com')
                new_anchor.set('style', 'color: #875A7B; text-decoration: none;')

                # Replace the old Odoo anchor with new Apptology anchor
                parent.replace(elem, new_anchor)

                # Clean up surrounding text that might reference Odoo
                previous = new_anchor.getprevious()
                if previous is not None:
                    if previous.tail and 'odoo' in previous.tail.lower():
                        previous.tail = ' '
                elif parent.text and 'odoo' in parent.text.lower():
                    parent.text = ' '

            # Replace any remaining text references
            for elem in tree.iter():
                if elem.text:
                    elem.text = re.sub(r'\bodoo\b', 'Apptology', elem.text, flags=re.IGNORECASE)
                if elem.tail:
                    elem.tail = re.sub(r'\bodoo\b', 'Apptology', elem.tail, flags=re.IGNORECASE)

            value = etree.tostring(
                tree, pretty_print=True, method="html", encoding="unicode"
            )

            if to_keep:
                value = value.replace("<body_msg></body_msg>", to_keep)

        if back_to_bytes:
            value = value.encode()
        elif back_to_markup:
            value = Markup(value)

        return value

    @api.model
    def _render_template(
            self,
            template_src,
            model,
            res_ids,
            engine="inline_template",
            add_context=None,
            options=None,
    ):
        """Replace Odoo branding with Apptology in templates
        If there's an <a> tag containing Odoo, replace it with Apptology branding

        :param str template_src: template text to render (jinja) or (qweb)
        :param str model: model name of records on which we want to perform rendering
        :param list res_ids: list of ids of records (all belonging to same model)
        :param string engine: inline_template, qweb or qweb_view
        :param add_context: additional context for rendering
        :param options: additional options for rendering

        :return dict: {res_id: string of rendered template based on record}"""
        original_rendered = super()._render_template(
            template_src,
            model,
            res_ids,
            engine=engine,
            add_context=add_context,
            options=options,
        )

        for key in res_ids:
            original_rendered[key] = self.replace_branding(original_rendered[key])

        return original_rendered
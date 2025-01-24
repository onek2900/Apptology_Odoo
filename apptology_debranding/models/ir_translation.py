
import re

from odoo import api, models, tools

from odoo.addons.base.models.ir_model import IrModelFields as IrModelFieldsOriginal

from .ir_config_parameter import get_debranding_parameters_env


def debrand_links(source, new_website):
    return re.sub(r"\bodoo.com\b", new_website, source)


def debrand(env, source, is_code=False):
    if not source or not re.search(r"\bodoo\b", source, re.IGNORECASE):
        return source
    params = get_debranding_parameters_env(env)
    new_name = params.get("apptology_debranding.new_name")
    new_website = params.get("apptology_debranding.new_website")

    source = debrand_links(source, new_website)

    source = re.sub(
        r"\b(?<!\.)odoo(?!\.\S|\s?=|\w|\[)\b", new_name, source, flags=re.IGNORECASE
    )

    return source


def debrand_bytes(env, source):
    if type(source) is bytes:
        source = source.decode("utf-8")
    return bytes(debrand(env, source), "utf-8")


class IrModelFields(models.Model):
    _inherit = "ir.model.fields"

    @api.model
    def _debrand_dict(self, res):
        for k in res:
            res[k] = self._debrand(res[k])
        return res

    @api.model
    def _debrand(self, source):
        return debrand(self.env, source)

    @api.model
    @tools.ormcache_context("model_name", keys=("lang",))
    def get_field_string(self, model_name):
        res = super(IrModelFields, self).get_field_string(model_name)
        return self._debrand_dict(res)

    @api.model
    @tools.ormcache_context("model_name", keys=("lang",))
    def get_field_help(self, model_name):
        res = super(IrModelFields, self).get_field_help(model_name)
        return self._debrand_dict(res)

    @api.model
    def decorated_clear_caches(self):
        """For calling clear_caches from via xml <function ... />
        we wrapped it in the api.model decorator

        """
        self.env.registry.clear_cache()

    @api.model
    @tools.ormcache_context("model_name", "field_name", keys=("lang",))
    def get_field_selection(self, model_name, field_name):

        selection = IrModelFieldsOriginal.get_field_selection.__wrapped__(
            self, model_name, field_name
        )
        return [(value, debrand(self.env, name)) for value, name in selection]

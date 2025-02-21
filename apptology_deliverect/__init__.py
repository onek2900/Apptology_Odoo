from . import controllers
from . import models
from odoo.fields import Command


def post_init_hook(env):
    deliverect_payment_method = env.ref("apptology_deliverect.pos_payment_method_deliverect")
    pos_config=env['pos.config'].search([])
    for config in pos_config:
        if not config.current_session_id.state:
            config.write({
                'payment_method_ids': [Command.link(deliverect_payment_method.id)]
            })


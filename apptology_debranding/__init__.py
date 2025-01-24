# -*- coding: utf-8 -*-

from . import models
from . import controllers
from . import translate


MODULE = "_apptology_debranding"


def uninstall_hook(env):
    env["ir.model.data"]._module_data_uninstall([MODULE])

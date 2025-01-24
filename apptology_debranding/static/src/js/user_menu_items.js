/** @odoo-module **/

import { registry } from "@web/core/registry";

const menuItems = registry.category("user_menuitems");
menuItems.remove("documentation");
menuItems.remove("support");
menuItems.remove("odoo_account");

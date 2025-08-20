/** @odoo-module */
/* global waitIndexDb */

import { patch } from "@web/core/utils/patch";
import { PosBus } from "@point_of_sale/app/bus/pos_bus_service";
import { _t } from "@web/core/l10n/translation";

patch(PosBus.prototype, {
    // Override
    dispatch(notif) {
        var self = this;
        super.dispatch(...arguments);
		if (notif.type == 'product_update') {
			if (notif.payload && notif.payload[0]) {
				const indexedDB = waitIndexDb(function () {
					resolve();
				});
				indexedDB.save_data('Products', [notif.payload[0]])
				var product_obj = self.pos.db.product_by_id[notif.payload[0].id]
				if (self && self && self.pos) {
					if (self.pos.config.sh_product_upate == 'online') {
						$.extend(product_obj, notif.payload[0]);
						if (product_obj === undefined){
							self.pos._addProducts([notif.payload[0].id]);
						}
					}
				}
			}
		}
		if (notif.type == 'customer_update') {
			if (notif.payload && notif.payload[0]) {
				const indexedDB = waitIndexDb(function () {
					resolve();
				});
				indexedDB.save_data('Customers', [notif.payload[0]])
				var partner_obj = self.pos.db.partner_by_id[notif.payload[0].id]
				if (self && self && self.pos) {
					if (self.pos.config.sh_partner_upate == 'online') {
						$.extend(partner_obj, notif.payload[0]);
						self.pos._loadPartners([notif.payload[0].id]);
					}
				}

			}

		}
    },
});

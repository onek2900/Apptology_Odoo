/** @odoo-module */
/* global waitIndexDb */

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { _t } from "@web/core/l10n/translation";

patch(PosStore.prototype, {

    async _processData(loadedData) {
        var self = this
        const customerModel = 'res.partner'
        if (localStorage.getItem('Customers') === 'loaded') {
            const result = await self.orm.silent.call("customer.update", "search_read",[]);
            if(result){
                for (const each of result) {
                    await waitIndexDb.get_by_id('Customers', parseInt(each['delete_ids'])).then(function (cache_partner) {
                        waitIndexDb.delete_item('Customers', parseInt(each['delete_ids']))
                    });
                }
            }

            var all_partners = []
            await waitIndexDb.get_all('Customers').then(function (cache_partners) {
                all_partners = cache_partners
            });
            loadedData['res.partner'] = all_partners
        } else {
            
            var all_partners = []
            const result = await self.orm.silent.call("pos.session", "sh_load_model",[odoo.pos_session_id, customerModel]);
            if (result) {
                all_partners = result
                const indexedDB = waitIndexDb(function () {
                    resolve();
                });
                indexedDB.save_data('Customers', all_partners)
            }
        }
        return await super._processData(...arguments);
    },
});

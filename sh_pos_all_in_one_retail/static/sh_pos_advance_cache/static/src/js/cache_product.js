/** @odoo-module */
/* global waitIndexDb */

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { _t } from "@web/core/l10n/translation";

patch(PosStore.prototype, {

    async _processData(loadedData) {
        var self = this
        const productModel = 'product.product'
        if (localStorage.getItem('Products') === 'loaded') {
            const result = await self.orm.silent.call("product.update", "search_read",[]);
            const indexedDB = waitIndexDb(function () {
                resolve();
            });
            if(result){
                for (const each of result) {
                    if ( parseInt(each['delete_ids']) ){
                        await indexedDB.get_by_id('Products', parseInt(each['delete_ids'])).then(function (cache_product) {
                            indexedDB.delete_item('Products', parseInt(each['delete_ids']))
                        });
                    }
                }
            }          
            var all_products = []
            await indexedDB.get_all('Products').then(function (cache_products) {
                all_products = cache_products
            });
            loadedData['product.product'] = all_products
            
        } else {
            var all_products = []
            const result = await self.orm.silent.call("pos.session", "sh_load_model",[odoo.pos_session_id, productModel]);
            if (result) {
                all_products = result
                const indexedDB = waitIndexDb(function () {
                    resolve();
                });
                indexedDB.save_data('Products', all_products)
            }
            loadedData['product.product'] = all_products
            localStorage.setItem('Products', 'loaded')
        }
        await super._processData(...arguments);
    },
});

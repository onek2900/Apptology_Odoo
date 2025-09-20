/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { patch } from "@web/core/utils/patch";
import { ReturnOrderPopup } from "@sh_pos_all_in_one_retail/static/sh_pos_order_return_exchange/apps/popups/return_order_popup/return_order_popup";


patch(ProductScreen.prototype, {
    async _barcodeProductAction(code) {
        var self = this;
        var scaned_code = code.base_code
        var barcode_order = await self.pos.db.order_by_barcode[scaned_code]
        if( barcode_order ){
            var order = barcode_order[0];
            var lines = barcode_order[1];
            console.log('lines',lines);
            const { confirmed } = await this.popup.add(ReturnOrderPopup, {
                title: _t("Return"),
                'order': order,
                'lines': lines,
                'sh_return_order': true,
                'exchange_order': true,
                'from_barcode' : true,
            });
            return false

        }else{
            await super._barcodeProductAction(...arguments)
        }
    }
})
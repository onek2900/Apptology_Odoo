/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { ProductQtyPopup } from "@sh_pos_all_in_one_retail/static/sh_pos_wh_stock/app/popups/product_stock_popup/product_stock_popup";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { _t } from "@web/core/l10n/translation";


patch(PosStore.prototype, {
    async _processData(loadedData) {
        await super._processData(...arguments);
        this.db.quant_by_product_id = {}
        if (loadedData['quant_by_product_id']) {
            this.db.quant_by_product_id = loadedData['quant_by_product_id']
        }
        if (loadedData['location_by_id']) {
            this.db.location_by_id = loadedData['location_by_id']
        }
    },
    async showStock(id) {
        event.stopPropagation()
        var stocks = this.db.get_stock_by_product_id(id)
        var TotalQty = 0.00
        if (stocks) {
            let Qtylst = stocks.map((stock) => stock.quantity)
            TotalQty = Qtylst.reduce((qty, next) => qty + next, 0);
        }
        var warehouse_by_id = {}
        if(stocks && stocks.length){
            if (this.config.sh_display_by == "warehouse") {
                for (let stock of stocks) {
                    if (stock.warehouse_id in warehouse_by_id) {
                        warehouse_by_id[stock.warehouse_id]['quantity'] += stock.quantity
                    } else {
                        warehouse_by_id[stock.warehouse_id] = { 'quantity': stock.quantity, 'name': stock.warehouse_name }
                    }
                }
                this.env.services.popup.add(ProductQtyPopup, {
                    title: _t("Product Stock"),
                    'product_stock': Object.values(warehouse_by_id),
                    'TotalQty': TotalQty
                });
            } else {
                this.env.services.popup.add(ProductQtyPopup, {
                    title: _t("Product Stock"),
                    'product_stock': stocks,
                    'TotalQty': TotalQty
                });
            }
        }else{
            await this.env.services.popup.add(ErrorPopup, {
                title: "Stock Warning",
                body: "Product has no stock !",
            });
        }
    },
   
})

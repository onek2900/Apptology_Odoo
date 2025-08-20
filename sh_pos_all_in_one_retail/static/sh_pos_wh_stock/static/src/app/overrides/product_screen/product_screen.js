/** @odoo-module */
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { patch } from "@web/core/utils/patch";
import { ProductStockRestrict } from "@sh_pos_all_in_one_retail/static/sh_pos_wh_stock/app/popups/restrict_sale_popup/restrict_sale_popup";
import { _t } from "@web/core/l10n/translation";

patch(ProductScreen.prototype, {
    _setValue(val) {
        var self = this;
        const selectedLine = this.currentOrder.get_selected_orderline();
        if (selectedLine && this.pos.config.sh_display_stock && this.pos.config.sh_show_qty_location) {
            const { numpadMode } = this.pos;
            if (numpadMode === "quantity") {
                var stocks = this.pos.db.get_stock_by_product_id(selectedLine.product.id)
                if (stocks) {
                    var location_id = this.pos.config.sh_pos_location ? this.pos.config.sh_pos_location[0] : false

                    var sh_stock = stocks.filter((stock) => stock.location_id == location_id)
                    var sh_min_qty = this.pos.config.sh_min_qty
                    if (sh_stock && selectedLine.product.type == "product") {
                        let qty = sh_stock[0].quantity - parseFloat(val)
                        if (sh_min_qty > qty) {
                            this.env.services.popup.add(ProductStockRestrict, {
                                title: _t(selectedLine.product.display_name),
                                body: _t('Minimum availabe quantity is ' + sh_min_qty),
                                'product': selectedLine.product,
                            }).then(function (callback) {
                                if (callback.confirmed) {
                                    selectedLine.set_quantity(val);
                                } else {
                                    self.numberBuffer.reset();
                                }
                            });
                        } else {
                            super._setValue(val);
                        }
                    } else {
                        super._setValue(val);
                    }
                } else {
                    super._setValue(val);
                }
            }else{
                super._setValue(val);
            }
        } else {
            super._setValue(val);
        }
    }
})

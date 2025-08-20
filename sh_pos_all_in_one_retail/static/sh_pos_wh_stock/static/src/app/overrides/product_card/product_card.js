/** @odoo-module */

import { ProductCard } from "@point_of_sale/app/generic_components/product_card/product_card";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";


patch(ProductCard.prototype, {
    setup(){
        super.setup()
        let product_id = this.props.productId
        var product = this.env.services.pos.db.product_by_id[product_id]
        this.default_code = product.default_code
        this.product_variant_count = product.product_variant_count
        this.type = product.type
    },
    get get_display_stock() {
        var product_id = this.props.productId
        var location_id = this.env.services.pos.config.sh_pos_location ? this.env.services.pos.config.sh_pos_location[0] : false
        var stocks = this.env.services.pos.db.get_stock_by_product_id(product_id)
        var qty = 0.00
        if (location_id && stocks && stocks.length) {
            var sh_stock = stocks.filter((stock) => stock.location_id == location_id)
            if (sh_stock && sh_stock.length) {
                qty = sh_stock[0].quantity
            }
        }
        return qty
    }
})

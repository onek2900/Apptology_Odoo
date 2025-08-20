/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";

export class ProductStockRestrict extends AbstractAwaitablePopup {
    static template = "sh_pos_wh_stock.ProductStockRestrict";
    setup() {
        super.setup();
    }
    confirm() {
        super.confirm()
    }
    get imageUrl() {
        const product = this.props.product;
        return `/web/image?model=product.product&field=image_128&id=${product.id}&unique=${product.write_date}`;
    }
}

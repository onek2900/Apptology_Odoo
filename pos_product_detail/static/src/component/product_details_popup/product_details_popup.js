/** @odoo-module */

import { ClosePosPopup } from "@point_of_sale/app/navbar/closing_popup/closing_popup";
import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";

export class ProductDetailsPopup extends AbstractAwaitablePopup {
    static template = "pos_product_detail.ProductDetailsPopup";
};

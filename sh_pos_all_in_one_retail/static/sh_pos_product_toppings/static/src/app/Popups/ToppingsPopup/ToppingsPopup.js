/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
import { usePos } from "@point_of_sale/app/store/pos_hook";
// import { ReceiptScreen } from "@point_of_sale/../tests/tours/helpers/ReceiptScreenTourMethods";
import { useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { formatFloat, formatMonetary } from "@web/views/fields/formatters";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";

export class ToppingsPopup extends AbstractAwaitablePopup {
    static template = "sh_pos_product_toppings.ToppingsPopup";
    setup() {
        super.setup();
        this.pos = usePos();
        this.numberBuffer = useService("number_buffer");
          this.popup = useService("popup");
        // useListener('click-topping-product', this._clicktoppigProduct);
    }
    ClickOk(){ 
        this.props.resolve({ confirmed: true, payload: null });
        this.cancel();
    }
    get globalToppings(){
        return this.props.Globaltoppings
    }
    get toppingProducts(){
        return this.props.Topping_products
    }
    get imageUrl() {
        const product = this.product; 
        return `/web/image?model=product.product&field=image_128&id=${product.id}&write_date=${product.write_date}&unique=1`;
    }
    get pricelist() {
        const current_order = this.pos.get_order();
        if (current_order) {
            return current_order.pricelist;
        }
        return this.pos.default_pricelist;
    }
    get price() {
        const { currencyId, digits } = this.env;
        const formattedUnitPrice = formatMonetary(this.product.get_price(this.pricelist, 1), { currencyId, digits });

        if (this.product.to_weight) {
            return `${formattedUnitPrice}/${
                this.pos.units_by_id[this.product.uom_id[0]].name
            }`;
        } else {
            return formattedUnitPrice;
        }
    }
    async _clicktoppigProduct(event){
        if (!this.pos.get_order()) {
            this.pos.add_new_order();
        }
        const product = event;
        if (this.pos.config.sh_enable_toppings && this.pos.get_order() && this.pos.get_order().get_selected_orderline()){
            this.pos.get_order().add_topping_product(product);
        }else{
            await this.popup.add(ErrorPopup, {
                title: 'Please Select Orderline !',
            });
            // await  this.popup.add(ErrorPopup, {title : 'Please Select Orderline !',body: '123'});
                
            // this.showPopup('ErrorPopup', { 
            //     title: 'Please Select Orderline !'
            // })
        }
        this.numberBuffer.reset();
    }
}
  
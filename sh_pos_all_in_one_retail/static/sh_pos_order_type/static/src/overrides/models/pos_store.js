/** @odoo-module */

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { Order , Orderline } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { OrderTypePopup } from "@sh_pos_all_in_one_retail/static/sh_pos_order_type/apps/popups/order_type_popup/order_type_popup"

patch(PosStore.prototype, {
    async _processData(loadedData) {
        await super._processData(...arguments);
        if (this.config.enable_order_type) {
            this.order_types = loadedData['sh.order.type'];
        }
    }
});

patch(Order.prototype, {
    setup(_defaultObj, options) {
        super.setup(...arguments)
        this.sh_set_order_type()
    },
    sh_set_order_type(){
        if(this.pos.config.enable_order_type){
            this.current_order_type = null
        }
        if (this.pos.config && this.pos.config.enable_order_type) {
            if (!this.pos.config.order_type_id && this.pos.config.order_type_mode == 'multi') {
                this.env.services.popup.add(OrderTypePopup);
            } 
            else{
                let ordertypes = Object.values(this.pos.order_types);
                const res = ordertypes.filter(type => type.id == this.pos.config.order_type_id[0])[0];
                this.current_order_type = res;
            }
        }
    },
    init_from_JSON(json){
        super.init_from_JSON(...arguments);
        if (json && json.sh_order_type_id) {
            const ordertype = this.pos.order_types.filter(type => type.id == json.sh_order_type_id)[0];
            this.set_order_type(ordertype)
        }
    },
    set_order_type(type){
        this.current_order_type = type 
        return this.current_order_type
    },
    get_order_type(){
        return this.current_order_type
    },        
    export_as_JSON() {
        var json = super.export_as_JSON(...arguments);
        if (this.current_order_type) {
            json.sh_order_type_id = this.get_order_type().id 
        }
        return json;
    }, 
    export_for_printing(){
        var res = super.export_for_printing()
        res["current_order_type"] = this.get_order_type()
        return res
    },
    async pay() {
        if(this.pos.config.enable_order_type){
            if (!this.pos.get_order().current_order_type ) {
                await this.env.services.popup.add(ErrorPopup, {
                    title: "Select order type",
                    body: "Order type is not selected please select the order type to continue...",
                });
                this.env.services.popup.add(OrderTypePopup);
            } else {
                if (this.pos.get_order().current_order_type.is_home_delivery && !this.pos.get_order().get_partner() && this.pos.config.enable_order_type) {
                    await this.env.services.popup.add(ErrorPopup, {
                        title: "Select customer for delivery order",
                        body: "Please select the customer for delivery order...",
                    });
                    const { confirmed: confirmedTempScreen, payload: newPartner } =
                        await this.pos.showTempScreen("PartnerListScreen");
                    if (!confirmedTempScreen) {
                        return;
                    }
                    this.pos.get_order().set_partner(newPartner);

                } else {
                    return super.pay(...arguments);
                }
            }
        }else{
            return super.pay(...arguments);

        }
      }
});

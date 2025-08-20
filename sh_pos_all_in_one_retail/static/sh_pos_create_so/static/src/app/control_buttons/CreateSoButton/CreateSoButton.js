/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { ShSOConfirmPopup } from "@sh_pos_all_in_one_retail/static/sh_pos_create_so/app/Popups/sh_so_confirm_popup/sh_so_confirm_popup";


export class CreateSoButton extends Component {
    static template = "sh_pos_create_so.CreateSoButton";
    setup() {
        this.pos = usePos();
        this.popup = useService("popup");
    }
    async onClick() {
        var self = this;
        var order = this.pos.get_order()
        var orderlines = order.get_orderlines()
        var client = order.get_partner();
        if (client != null) {
            var property_payment_term_id = false
            if (client && client.property_supplier_payment_term_id) {
                property_payment_term_id = client.property_supplier_payment_term_id[0]
            }
            if (orderlines.length != 0) {
                try {
                    var orderLines = []
                    order.orderlines.forEach(item => {
                        return orderLines.push(item.export_as_JSON());
                    });
                    var CreateSo = {
                        'partner_id': order.get_partner().id,
                        'payment_term_id': property_payment_term_id,
                        'order_lines': orderLines,
                    }

                    self.pos.db.all_sale_orders.push(CreateSo)

                    var Orders = await this.pos.create_sale_order()
                    if (Orders && Orders.length > 0) { 
                        self.popup.add(ShSOConfirmPopup, {
                            title: 'Sale Order Reference',
                            body: " Sale Order Created.",
                            SaleOrderId: Orders[0].id,
                            SaleOrderName: Orders[0].name
                        })
                    }

                } catch (error) {
                    this.pos.set_synch('disconnected');
                }
            }
            else {
                this.popup.add(ErrorPopup, {
                    title: 'Product is not available !',
                    body: 'Please Add Product In Cart !',
                });
            }
        }
        else {
            this.popup.add(ErrorPopup, {
                title: 'Partner is not available !',
                body: 'Please Select Partner!',
            });
        }
    }
}

ProductScreen.addControlButton({
    component: CreateSoButton,
    condition: function () {
        return this.pos.config.sh_display_sale_btn
    },
})

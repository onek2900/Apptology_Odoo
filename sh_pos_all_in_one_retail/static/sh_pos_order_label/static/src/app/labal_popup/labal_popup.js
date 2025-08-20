/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useState, onMounted } from "@odoo/owl";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { Orderline } from "@point_of_sale/app/store/models";

export class LabelPopup extends 
AbstractAwaitablePopup {
    static template = "sh_pos_order_label.LabelPopup";
    setup() {
        super.setup();
        this.section = 'Section' || "";
        this.pos = usePos();
        this.state = useState({
            value: null
        });
        onMounted(() => {
            $('#label_value').focus()
        })
    }
    confirm() {
        var self = this
        var value = this.state.value
        if (value) {
            var order = this.pos.get_order()
            var product = this.pos.get_orderline_product()
            var selected_line = order.get_selected_orderline()
            if (order && product) {
                var line = new Orderline({ env: this.env },
                    {
                        pos: self.pos,
                        order: order,
                        product: product,
                    })
                line.set_orderline_label(value)
                order.add_orderline(line);
            }
            order.select_orderline(selected_line);
            super.confirm()
        } else {
            super.cancel()
            self.pos.popup.add(ErrorPopup, {
                title: _t('Label Not Found !'),
                body: _t('Please Add Label')
            })
        }
    }
}

/** @odoo-module */

import { usePos } from "@point_of_sale/app/store/pos_hook";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { TemplateGlobalNotePopupWidget } from "@sh_pos_all_in_one_retail/static/sh_pos_note/apps/popups/template_global_note_popup/template_global_note_popup";

export class GlobalNoteButton extends Component {
    static template = "point_of_sale.GlobalNoteButton";

    setup() {
        super.setup();
        this.pos = usePos();
        this.popup = useService("popup");
    }
    onClickGlobalNote() {
        if (this.pos.get_order().get_selected_orderline()) {
            var PreDefineNotes = Object.values(this.pos.pre_defined_note_data_dict)
            let { confirmed, payload } = this.popup.add(TemplateGlobalNotePopupWidget,{
                'pre_defined_note_data_dict' : PreDefineNotes
            });
            if (!confirmed) {
                return;
            }
        } else {
            this.popup.add(ErrorPopup, {
                title:  'Empty Order',
                body: 'Please select the product!',
            })
        }
    }
}

ProductScreen.addControlButton({
    component: GlobalNoteButton,
    condition: function () {
        return this.pos.config.enable_order_note;
    },
});

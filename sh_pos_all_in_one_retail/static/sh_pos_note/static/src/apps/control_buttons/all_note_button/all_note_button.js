/** @odoo-module */

import { usePos } from "@point_of_sale/app/store/pos_hook";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { Component } from "@odoo/owl";

export class AllNoteButton extends Component {
    static template = "sh_pos_note.AllNoteButton";

    setup() {
        super.setup();
        this.pos = usePos();
    }
    async onClickAlllineNote() {

        var PreDefineNotes = Object.values(this.pos.pre_defined_note_data_dict)

        const { confirmed, payload } = await this.pos.showTempScreen("AllNoteScreen",{
            'pre_defined_note_data': PreDefineNotes
        });
        
    }
}

ProductScreen.addControlButton({
    component: AllNoteButton,
    condition: function () {
        return true;
    },
});

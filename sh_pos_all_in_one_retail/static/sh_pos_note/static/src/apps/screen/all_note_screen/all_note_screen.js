/** @odoo-module **/

import { registry } from "@web/core/registry";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";
import { TemplatePreDefineNoteLine } from "@sh_pos_all_in_one_retail/static/sh_pos_note/apps/screen/all_note_screen/template_pre_define_note_line/template_pre_define_note_line";
import { CreateNotePopupWidget } from "@sh_pos_all_in_one_retail/static/sh_pos_note/apps/popups/create_note_popup/create_note_popup";

export class AllNoteScreen extends Component {
    static template = "sh_pos_note.AllNoteScreen";
    static components = { TemplatePreDefineNoteLine };
    setup() {
        this.pos = usePos();
        this.popup = useService("popup");
    }
    back() {
            this.pos.closeTempScreen();
    }
    onClickGlobalNoteScreen() {
        this.popup.add(CreateNotePopupWidget);
    }

}
registry.category("pos_screens").add("AllNoteScreen", AllNoteScreen);

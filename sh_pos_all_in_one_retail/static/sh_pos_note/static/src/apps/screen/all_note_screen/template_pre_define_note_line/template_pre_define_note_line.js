/** @odoo-module **/

import { registry } from "@web/core/registry";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";

export class TemplatePreDefineNoteLine extends Component {
    static template = "sh_pos_note.TemplatePreDefineNoteLine";
    setup() {
        this.pos = usePos();
        this.orm = useService("orm");
        this.popup = useService("popup");
    }
    async delete_note(event) {
        var self = this;
        var note_id = $(event.currentTarget).data("id");
        var result = await this.orm.call("pre.define.note", "unlink",[[note_id]])
        if(result){
            var pre_defined_note_data = self.pos.pre_defined_note_data_dict
            delete pre_defined_note_data[note_id];
            self.pos.showTempScreen("AllNoteScreen",{
                'pre_defined_note_data': Object.values(pre_defined_note_data)
            })
        }
    }
    async edit_note(event) {
        $(event.currentTarget).closest("tr").find(".input_name")[0].classList.add("show_input_name");
        $(event.currentTarget).closest("tr").find(".note_name")[0].classList.add("hide_note_name");            
    }
    async save_note(event) {
        var self = this;
        $(event.currentTarget).closest("tr").find(".input_name")[0].classList.remove("show_input_name");
        $(event.currentTarget).closest("tr").find(".note_name")[0].classList.remove("hide_note_name");
        var note_id = $(event.currentTarget).data("id");
        var pre_defined_note_data = self.pos.pre_defined_note_data_dict
        var current_dict = pre_defined_note_data[note_id]
        var new_note = $(event.currentTarget).closest("tr").find(".input_tag_name")[0].value
        current_dict.name = $(event.currentTarget).closest("tr").find(".input_tag_name")[0].value
        pre_defined_note_data[note_id] = current_dict
        var result = await this.orm.call("pre.define.note", "write",[note_id,{'name' : new_note}])
        if(result){
            self.pos.showTempScreen("AllNoteScreen",{
                'pre_defined_note_data': Object.values(pre_defined_note_data)
            })
        }
    }

}
registry.category("pos_screens").add("TemplatePreDefineNoteLine", TemplatePreDefineNoteLine);

/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class TemplateLineNotePopupWidget extends AbstractAwaitablePopup {
    static template = "sh_pos_note.TemplateLineNotePopupWidget";
    setup() {
        super.setup();
        this.pos = usePos();
        this.orm = useService("orm");
        this.value = useState({
            notes :  "",
            store_checkbox : false
        })
    }
    async confirm() {
        var self = this;
        // self.props.resolve({ confirmed: true, payload: await self.getPayload() });
        self.pos.get_order().get_selected_orderline().set_line_note(this.value.notes);

        if (self.pos.config.hide_extra_note_checkbox && this.value.store_checkbox) {
            var value = this.value.notes
            var added_note = value.split(",");
          
            for(var i=0 ; i<added_note.length;i++){
                var each_added_note = added_note[i]
                
                if (!self.pos.db.all_note_names.includes(each_added_note)) {
                    var result = await this.orm.call("pre.define.note", "sh_create_note",[{'name' : each_added_note}])

                    var pre_defined_note_data = self.pos.pre_defined_note_data_dict
                    pre_defined_note_data[result.id] = result
                }
            }
        }
        self.cancel()
    }
    set_note(val){
        if($("#textarea_note").val() && $("#textarea_note").val() != ""){
            $("#textarea_note").val($("#textarea_note").val() + "," + val);
        }
        else{
            $("#textarea_note").val(val);
        }
        return $("#textarea_note").val()
    }
    async click_line_note_button(event) {
        var added_note;
        var value = $(event.currentTarget).data("value");
        if ($(event.currentTarget).hasClass("selected")) {
            $(event.currentTarget).removeClass("selected");
            added_note = $("#textarea_note")[0].value.split(",");
            for (var i = 0; i < added_note.length; i++) {
                if (added_note[i] == value) {
                    added_note.splice(i, 1);
                }
            }
            if (added_note.length > 0) {
                if (added_note.length == 1) {
                    $("#textarea_note").val(added_note[0]);
                } else {
                    var new_line_note = "";
                    var added_note_length = added_note.length;
                    for (var i = 0; i < added_note.length; i++) {
                        if (i + 1 == added_note_length) {
                            new_line_note += added_note[i];
                        } else {
                            new_line_note += added_note[i] + ",";
                        }
                    }

               
                let val = this.set_note(new_line_note);
                  this.value.notes = val
                }
            } else {
                $("#textarea_note").val("");
            }
        } else {
            $(event.currentTarget).addClass("selected");
            let val = this.set_note(value );
            this.value.notes = val
           
        }
    }
    
}

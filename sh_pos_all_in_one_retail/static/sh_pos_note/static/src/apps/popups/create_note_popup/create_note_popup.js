/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useState } from "@odoo/owl";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { useService } from "@web/core/utils/hooks";

export class CreateNotePopupWidget extends AbstractAwaitablePopup {
    static template = "sh_pos_note.CreateNotePopupWidget";
    
    setup() {
        super.setup();
        this.pos = usePos();
        this.orm = useService("orm");
        this.popup = useService("popup");
        this.value = useState({
            notes :  "",
        })
    }
    async confirm() {
        var self = this;
        var value = this.value.notes;
        if(value && value != ""){          
            var result = await this.orm.call("pre.define.note", "sh_create_note",[{'name' : value}])
            if(result){

            }
            var pre_defined_note_data = self.pos.pre_defined_note_data_dict
            pre_defined_note_data[result.id] = result
                    
            self.pos.showTempScreen("AllNoteScreen",{
                'pre_defined_note_data': Object.values(pre_defined_note_data)
            })
            super.confirm()
        }else{
            this.popup.add(ErrorPopup, {
                title:  'Empty Name',
                body: 'Name should not be blank!',
            })
            $("#textarea_note")[0].classList.add("name_not_valid");
        }
    }
 
}

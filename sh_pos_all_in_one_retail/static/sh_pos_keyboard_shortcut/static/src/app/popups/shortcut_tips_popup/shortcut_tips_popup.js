/** @odoo-module */
    
    
import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
import { usePos } from "@point_of_sale/app/store/pos_hook";
   
export class ShortcutTipsPopup extends AbstractAwaitablePopup {
    static template = "sh_pos_all_in_one_retail.ShortcutTipsPopup";
        setup() {
            super.setup();
            this.pos = usePos();
        } 
    }

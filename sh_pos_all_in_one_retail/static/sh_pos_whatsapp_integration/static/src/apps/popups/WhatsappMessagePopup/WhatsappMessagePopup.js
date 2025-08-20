/** @odoo-module */

import { usePos } from "@point_of_sale/app/store/pos_hook";
import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";

export class WhatsappMessagePopup extends AbstractAwaitablePopup {
    static template = "sh_pos_whatsapp_integration.WhatsappMessagePopup";    

    setup() {
        super.setup(...arguments);
    }
}

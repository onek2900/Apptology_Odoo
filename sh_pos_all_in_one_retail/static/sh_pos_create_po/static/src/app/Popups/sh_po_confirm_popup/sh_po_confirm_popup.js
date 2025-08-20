/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
import { usePos } from "@point_of_sale/app/store/pos_hook";

// formerly ConfirmPopupWidget
export class ShPOConfirmPopup extends AbstractAwaitablePopup {
    static template = "sh_pos_create_po.ShPOConfirmPopup";
    static defaultProps = {
        confirmText: _t("Confirm"),
        cancelText: _t("Discard"),
        title: _t("Abc"),
    };
    setup(){
        super.setup()
        this.pos = usePos();
    }
    confirm() {
        super.confirm()
        var self = this;
        var orderlines = self.pos.get_order().get_orderlines()
        let res = [...orderlines].map(async(line)=>await self.pos.get_order().removeOrderline(line))
        this.pos.db.remove_all_purchase_orders()
        return res
    }
}

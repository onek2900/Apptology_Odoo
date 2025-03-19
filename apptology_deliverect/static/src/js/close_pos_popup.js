/** @odoo-module */

import { ClosePosPopup } from "@point_of_sale/app/navbar/closing_popup/closing_popup";
import { patch } from "@web/core/utils/patch";
import { useState } from "@odoo/owl";
import { ConfirmPopup } from "@point_of_sale/app/utils/confirm_popup/confirm_popup";
import { _t } from "@web/core/l10n/translation";

patch(ClosePosPopup.prototype, {
    setup() {
        super.setup();
        this.state = useState({ ...this.state, unFinalizedOrdersCount: 0 });
        this.isOrderFinalized();
    },
    async isOrderFinalized() {
        this.state.unFinalizedOrdersCount = await this.orm.searchCount(
                    "pos.order",
                    [["config_id", "=", this.pos.config.id],['session_id','=',this.pos.config.current_session_id[0]],
                    ["is_online_order", "=", true],["online_order_status", "=", "approved"],["order_status", "!=",
                    "cancel"]]);
        console.log(this.pos.config.current_session_id[0])
        var records = await this.orm.searchRead(
                    "pos.order",
                    [["config_id", "=", this.pos.config.id],['session_id','=',this.pos.config.current_session_id[0]],
        ["is_online_order", "=", true]],['name','config_id','online_order_status','order_status'])
        console.log("RECORDS :",records)
    },
        //@override
    async confirm() {
        if (this.state.unFinalizedOrdersCount){
            const { confirmed } = await this.popup.add(ConfirmPopup, {
                    title: _t("Warning"),
                    body: _t(
                        "There are unfinalized online orders. It is recommended to finalize these orders before closing the session. Are you sure you want to proceed?"
                    ),
                    confirmText: _t("Proceed"),
                    cancelText: _t("Discard"),
                });
                if (confirmed) {
                    if (!this.pos.config.cash_control || this.env.utils.floatIsZero(this.getMaxDifference())) {
                        await this.closeSession();
                        return;
                    }
                    if (this.hasUserAuthority()) {
                        const { confirmed } = await this.popup.add(ConfirmPopup, {
                            title: _t("Payments Difference"),
                            body: _t(
                                "Do you want to accept payments difference and post a profit/loss journal entry?"
                            ),
                        });
                    if (confirmed) {
                        await this.closeSession();
                    }
                    return;
                    }
                    await this.popup.add(ConfirmPopup, {
                        title: _t("Payments Difference"),
                        body: _t(
                            "The maximum difference allowed is %s.\nPlease contact your manager to accept the closing difference.",
                            this.env.utils.formatCurrency(this.props.amount_authorized_diff)
                        ),
                        confirmText: _t("OK"),
                    });
                }
            }
        else{
            if (!this.pos.config.cash_control || this.env.utils.floatIsZero(this.getMaxDifference())) {
                await this.closeSession();
                return;
            }
            if (this.hasUserAuthority()) {
                const { confirmed } = await this.popup.add(ConfirmPopup, {
                    title: _t("Payments Difference"),
                    body: _t(
                        "Do you want to accept payments difference and post a profit/loss journal entry?"
                    ),
                });
            if (confirmed) {
                await this.closeSession();
            }
            return;
            }
            await this.popup.add(ConfirmPopup, {
                title: _t("Payments Difference"),
                body: _t(
                    "The maximum difference allowed is %s.\nPlease contact your manager to accept the closing difference.",
                    this.env.utils.formatCurrency(this.props.amount_authorized_diff)
                ),
                confirmText: _t("OK"),
            });
        }
    }
});
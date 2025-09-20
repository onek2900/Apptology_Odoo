/** @odoo-module */

import { ClosePosPopup } from "@point_of_sale/app/navbar/closing_popup/closing_popup";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

patch(ClosePosPopup.prototype, {
    setup() {
        super.setup();
        this.action = useService("action");
        this.notification = useService("notification");
    },

    async printClosureReport() {
        const sessionId = this.pos?.pos_session?.id;
        if (!sessionId) {
            this.notification.add(_t("The session is not available."), { type: "warning" });
            return;
        }

        try {
            const action = await this.orm.call(
                "pos.session",
                "action_print_closure_report",
                [[sessionId]],
            );
            if (!action) {
                this.notification.add(
                    _t("No closure report is configured for this session."),
                    { type: "warning" },
                );
                return;
            }
            await this.action.doAction(action);
        } catch (error) {
            console.error("Failed to print session closure report", error);
            this.notification.add(
                _t("Unable to print the session closure report."),
                { type: "danger" },
            );
        }
    },
});

/** @odoo-module */

import { Navbar } from "@point_of_sale/app/navbar/navbar";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

patch(Navbar.prototype, {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.notification = useService("notification");
        this._monerisSyncPending = false;
    },

    async monerisSyncNow() {
        if (this._monerisSyncPending) return;
        this._monerisSyncPending = true;
        this.notification.add(_t("Requesting Moneris sync…"), { type: "info" });
        const cfgId = this.pos.config.id;
        const sessionId = this.pos?.pos_session?.id;
        try {
            await this.orm.call(
                "pos.payment.method",
                "action_moneris_sync_now_for_config",
                [cfgId, sessionId]
            );
            this.notification.add(_t("Moneris sync requested"), { type: "info" });
        } catch (e) {
            console.error("Moneris sync request failed", e);
            this.notification.add(_t("Failed to request Moneris sync"), { type: "danger", sticky: true });
        } finally {
            this._monerisSyncPending = false;
        }
    },
});

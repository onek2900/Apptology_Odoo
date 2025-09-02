/** @odoo-module */

import { Navbar } from "@point_of_sale/app/navbar/navbar";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { onWillUnmount } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";

patch(Navbar.prototype, {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.notification = useService("notification");
        this._monerisSyncPending = false;

        // Listen for Moneris sync completion on a per-config channel
        this.busService = this.env.services.bus_service;
        this.monerisChannel = `pos_moneris_${this.pos.config.id}`;
        this.busService.addChannel(this.monerisChannel);
        this._onNotif = ({ detail: notifications }) => {
            const events = notifications.filter(
                (n) => (n.payload?.channel === this.monerisChannel)
            );
            for (const evt of events) {
                const payload = evt.payload;
                const msg = payload?.message || payload;
                if (!msg) continue;
                if (msg.type === 'sync_success') {
                    this.notification.add(_t("Moneris terminal synced successfully."), { type: "info" });
                } else if (msg.type === 'sync_failed') {
                    const reason = msg.statusCode ? ` (code ${msg.statusCode})` : "";
                    this.notification.add(_t("Moneris terminal sync failed") + reason, { type: "danger", sticky: true });
                } else if (msg.type === 'terminal_error' || (msg.status && String(msg.status).toLowerCase().includes('error'))) {
                    const ed = Array.isArray(msg.errorDetails) && msg.errorDetails.length ? `: ${msg.errorDetails[0].issue || msg.errorDetails[0].errorCode}` : '';
                    const code = msg.statusCode ? ` (code ${msg.statusCode})` : '';
                    this.notification.add(_t("Moneris terminal error") + ed + code, { type: "danger", sticky: true });
                }
            }
        };
        this.busService.addEventListener('notification', this._onNotif);
        onWillUnmount(() => {
            if (this._onNotif) this.busService.removeEventListener('notification', this._onNotif);
            if (this.monerisChannel) this.busService.deleteChannel(this.monerisChannel);
        });
    },

    async monerisSyncNow() {
        if (this._monerisSyncPending) return;
        this._monerisSyncPending = true;
        this.notification.add(_t("Requesting Moneris sync…"), { type: "info" });
        const cfgId = this.pos.config.id;
        const sessionId = this.pos?.pos_session?.id;
        try {
            const resp = await this.orm.call(
                "pos.payment.method",
                "action_moneris_sync_now_for_config",
                [cfgId, sessionId]
            );
            // Inspect immediate HTTP response for known terminal issues
            const results = resp && resp.results || [];
            let anyError = false;
            for (const it of results) {
                const first = it?.resp?.receipt?.data?.response?.[0];
                if (first && (String(first.status || '').toLowerCase().includes('error') || String(first.statusCode || '').startsWith('59'))) {
                    anyError = true;
                    const code = first.statusCode ? ` (code ${first.statusCode})` : '';
                    this.notification.add(_t("Moneris terminal error") + `: ${first.status || 'Unknown'}` + code, { type: "danger", sticky: true });
                }
            }
            if (!anyError) {
                this.notification.add(_t("Moneris sync requested"), { type: "info" });
            }
        } catch (e) {
            console.error("Moneris sync request failed", e);
            this.notification.add(_t("Failed to request Moneris sync"), { type: "danger", sticky: true });
        } finally {
            this._monerisSyncPending = false;
        }
    },
});

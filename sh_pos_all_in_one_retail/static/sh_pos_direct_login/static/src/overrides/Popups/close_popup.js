/** @odoo-module */

import { _t } from "@web/core/l10n/translation";
import { ClosePosPopup } from "@point_of_sale/app/navbar/closing_popup/closing_popup";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { ConnectionLostError, ConnectionAbortedError } from "@web/core/network/rpc_service";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";

patch(ClosePosPopup.prototype, {
    setup(){
        super.setup(...arguments)
        this.orm = useService("orm");
    },
    async closeSession() {
        if (this.pos.user && this.pos.user.sh_is_direct_logout) {
            if (this.pos.config.cash_control) {
                const response = await this.orm.call(
                    "pos.session",
                    "post_closing_cash_details",
                    [this.pos.pos_session.id],
                    {
                        counted_cash: parseFloat(
                            this.state.payments[this.props.default_cash_details.id].counted
                        ),
                    }
                );
    
                if (!response.successful) {
                    return this.handleClosingError(response);
                }
            }
    
            try {
                await this.orm.call("pos.session", "update_closing_control_state_session", [
                    this.pos.pos_session.id,
                    this.state.notes,
                ]);
            } catch (error) {
                // We have to handle the error manually otherwise the validation check stops the script.
                // In case of "rescue session", we want to display the next popup with "handleClosingError".
                // FIXME
                if (!error.data && error.data.message !== "This session is already closed.") {
                    throw error;
                }
            }
    
            try {
                const bankPaymentMethodDiffPairs = this.props.other_payment_methods
                    .filter((pm) => pm.type == "bank")
                    .map((pm) => [pm.id, this.getDifference(pm.id)]);
                const response = await this.orm.call("pos.session", "close_session_from_ui", [
                    this.pos.pos_session.id,
                    bankPaymentMethodDiffPairs,
                ]);
                if (!response.successful) {
                    return this.handleClosingError(response);
                }
                window.location.href = "/web/login";
            } catch (error) {
                if (error instanceof ConnectionLostError) {
                    // Cannot redirect to backend when offline, let error handlers show the offline popup
                    // FIXME POSREF: doing this means closing again when online will redo the beginning of the method
                    // although it's impossible to close again because this.closeSessionClicked isn't reset to false
                    // The application state is corrupted.
                    throw error;
                } else {
                    // FIXME POSREF: why are we catching errors here but not anywhere else in this method?
                    await this.popup.add(ErrorPopup, {
                        title: _t("Closing session error"),
                        body: _t(
                            "An error has occurred when trying to close the session.\n" +
                                "You will be redirected to the back-end to manually close the session."
                        ),
                    });
                    window.location.href = "/web/login";
                }
            }
        
        } else {
            super.closeSession();
        }
    }
});



/** @odoo-module */
import { PaymentInterface } from "@point_of_sale/app/payment/payment_interface";
import { _t } from "@web/core/l10n/translation";
import { AlertDialog, ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";

export class PaymentMoneris extends PaymentInterface {
    setup() {
        super.setup(...arguments);
        this.paymentNotificationResolver = null;
    }

    send_payment_request(cid) {
        super.send_payment_request(cid);
        return this._moneris_pay(cid);
    }

    _moneris_pay(cid) {
        const order = this.pos.get_order();
        const line = order.selected_paymentline;

        if (line.amount < 0) {
            this._show_error(_t("Cannot process negative payment amounts."));
            return Promise.resolve();
        }

        const paymentData = this._moneris_payment_data(order, line);

        // To prevent canceling the payment while the order is being created
        if (line.payment_status !== "force_done" && line.payment_status !== "waitingCard") {
            line.set_payment_status("waitingCapture");
        }
        
        return this._call_moneris(paymentData, 'order').then((response) => {
            return this._handle_moneris_response(response);
        });
    }

    _moneris_payment_data(order, line) {
        return {
            posSessionID:order.pos_session_id,
            orderId:order.name,
            orderAmount:line.amount

        };
    }

    _call_moneris(data, operation) {
        return this.env.services.orm.silent.call("pos.payment.method", "send_moneris_payment", [
                [this.payment_method.id],
                data,
            ])
            .catch(this._handle_connection_failure.bind(this));
            // .catch((error) => this._handle_connection_failure(error));
    }

    _handle_connection_failure(data ={}) {
        console.log('handling connection failure')
    }

    async _handle_moneris_response(response) {
        console.log('handle Moneris response :',response)
        const line = this.pending_moneris_line();
        if (!line) {
            this._show_error(_t("No pending Moneris payment line found."));
            return false;
        }

        if(!response){
            this._show_error(_t("An error occured while processing the payment, Please try again"));
            line.set_payment_status('force_done');
            return false;
        }

        if (response.error && response.error.status_code === 400) {
            this._show_error(_t(response.error.message));
            line.set_payment_status('force_done');
            return false;
        } else if (response.error) {
            this._show_error(_t(response.error.message));
            line.set_payment_status('force_done');
            return false;
        }


        line.set_payment_status("waitingCard");
        // Ensure any previous timer is cleared
        this._clearCancelTimer();
        // Start a 5s timer to allow user to cancel if terminal takes long
        this._cancelTimeoutId = setTimeout(() => {
            // Guard: payment could have finished already
            const cur = this.pending_moneris_line();
            if (!cur || cur.get_payment_status() === 'done') return;
        }, 5000);

        return await new Promise((resolve) => {
            this.paymentNotificationResolver = resolve;
        });
    }

    _clearCancelTimer() {
        if (this._cancelTimeoutId) {
            clearTimeout(this._cancelTimeoutId);
            this._cancelTimeoutId = null;
        }
    }

    pending_moneris_line() {
        return this.pos.getPendingPaymentLine("moneris");
    }

    _showMsg(msg, title) {
        this.env.services.dialog.add(AlertDialog, {
            title: "Moneris " + title,
            body: msg,
        });
    }

    _show_error(msg) {
        this.env.services.dialog.add(AlertDialog, {
            title: _t("Moneris Error"),
            body: msg,
        });
    }

}

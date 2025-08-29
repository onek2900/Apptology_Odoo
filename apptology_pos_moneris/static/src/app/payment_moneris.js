/** @odoo-module */
import { PaymentInterface } from "@point_of_sale/app/payment/payment_interface";
import { _t } from "@web/core/l10n/translation";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";

export class PaymentMoneris extends PaymentInterface {
    setup() {
        super.setup(...arguments);
        this.paymentNotificationResolver = null;
        this.pollingInterval = null;
        this.currentOrderUid = null;
        this.receiptUrl = null;
        this.isTerminalSynced = false;
        this._startPolling();
    }

    willUnmount() {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
        }
        super.willUnmount();
    }

    send_payment_request(cid) {
        super.send_payment_request(cid);
        return this._moneris_pay(cid);
    }

    async _moneris_pay(cid) {
        const order = this.pos.get_order();
        if (!order) {
            this._show_error(_t("No active order found."));
            return Promise.resolve(false);
        }

        const line = order.selected_paymentline;
        if (!line) {
            this._show_error(_t("No payment line selected."));
            return Promise.resolve(false);
        }

        if (line.amount <= 0) {
            this._show_error(_t("Cannot process zero or negative payment amounts."));
            return Promise.resolve(false);
        }

        // Check if terminal needs sync
        if (!this.isTerminalSynced) {
            const syncResult = await this._syncTerminal();
            if (!syncResult) {
                this._show_error(_t("Terminal synchronization failed. Please try again."));
                return false;
            }
            this.isTerminalSynced = true;
        }

        // Store current order UID for later reference
        this.currentOrderUid = order.uid;
        this.receiptUrl = null;

        const paymentData = this._moneris_payment_data(order, line);

        if (line.payment_status !== "force_done" && line.payment_status !== "waitingCard") {
            line.set_payment_status("waitingCapture");
        }

        return this._call_moneris(paymentData).then((response) => {
            return this._handle_moneris_response(response, line);
        }).catch((error) => {
            console.error('Moneris payment error:', error);
            if (line) {
                line.set_payment_status('force_done');
            }
            this._show_error(_t("Payment processing failed. Please try again."));
            return false;
        });
    }

    async _syncTerminal() {
        try {
            this._showMsg(_t("Synchronizing terminal with Moneris..."), "Sync");

            const response = await this.env.services.orm.silent.call(
                "pos.payment.method",
                "sync_moneris_terminal",
                [[this.payment_method.id]]
            );

            if (response && response.success) {
                console.log('Terminal sync successful');
                this._showMsg(_t("Terminal synchronized successfully!"), "Success");
                return true;
            } else if (response && response.error) {
                this._show_error(_t(response.error.message || "Terminal sync failed"));
                return false;
            } else {
                this._show_error(_t("Terminal sync failed. Please check configuration."));
                return false;
            }
        } catch (error) {
            console.error('Terminal sync error:', error);
            this._show_error(_t("Terminal synchronization error"));
            return false;
        }
    }

    _moneris_payment_data(order, line) {
        return {
            posSessionID: order.pos_session_id,
            orderId: order.name,
            orderAmount: line.amount
        };
    }

    _call_moneris(data) {
        return this.env.services.orm.silent.call(
            "pos.payment.method",
            "send_moneris_payment",
            [[this.payment_method.id], data]
        ).catch(this._handle_connection_failure.bind(this));
    }

    _handle_connection_failure(error) {
        console.error('Moneris connection failure:', error);
        this._show_error(_t("Connection to payment gateway failed. Please try again."));
        return { error: { message: "Connection failed" } };
    }

    async _handle_moneris_response(response, line) {
        console.log('Moneris response received:', response);

        if (!line) {
            this._show_error(_t("Payment line not found."));
            return false;
        }

        if (!response) {
            this._show_error(_t("An error occurred while processing the payment. Please try again"));
            line.set_payment_status('force_done');
            return false;
        }

        if (response.error) {
            this._show_error(_t(response.error.message || "Payment error occurred"));
            line.set_payment_status('force_done');
            return false;
        }

        // Check the initial response and get receipt URL
        const transactionResponse = response.receipt?.data?.response?.[0];
        if (transactionResponse) {
            const statusCode = transactionResponse.statusCode;
            const completed = transactionResponse.completed === "true";

            console.log('Initial transaction status:', { statusCode, completed });

            // Store receipt URL for polling
            this.receiptUrl = transactionResponse.receiptUrl;
            line.moneris_transaction_id = transactionResponse.cloudTicket || '';

            if (statusCode === "5201" && !completed && this.receiptUrl) {
                // Transaction request received, start polling receipt URL
                line.set_payment_status("waitingCard");
                return await this._waitForPaymentCompletion(line);
            } else if (statusCode === "5207" && completed) {
                // Already approved
                line.set_payment_status("done");
                this._storeTransactionDetails(line, response);
                return true;
            } else if (["5206", "5453"].includes(statusCode)) {
                // Declined or not completed
                this._show_error(_t("Payment was declined. Please try another payment method."));
                line.set_payment_status('force_done');
                return false;
            }
        }

        this._show_error(_t("Unexpected response from payment gateway"));
        line.set_payment_status('force_done');
        return false;
    }

    async _waitForPaymentCompletion(line, maxAttempts = 60, interval = 2000) {
        return new Promise((resolve) => {
            if (!line || !this.receiptUrl) {
                resolve(false);
                return;
            }

            let attempts = 0;

            const checkStatus = async () => {
                attempts++;
                try {
                    const status = await this._check_receipt_status();

                    // Check if line still exists and belongs to current order
                    if (!this._isValidPaymentLine(line)) {
                        clearInterval(checkInterval);
                        resolve(false);
                        return;
                    }

                    switch (status) {
                        case 'approved':
                            clearInterval(checkInterval);
                            line.set_payment_status('done');
                            this._storeTransactionDetailsFromPolling(line);
                            resolve(true);
                            break;

                        case 'declined':
                        case 'failed':
                            clearInterval(checkInterval);
                            this._show_error(_t("Payment was declined or failed"));
                            line.set_payment_status('force_done');
                            resolve(false);
                            break;

                        case 'pending':
                            // Continue polling
                            if (attempts >= maxAttempts) {
                                clearInterval(checkInterval);
                                this._show_error(_t("Payment timeout. Please try again"));
                                line.set_payment_status('force_done');
                                resolve(false);
                            }
                            break;

                        default:
                            if (attempts >= maxAttempts) {
                                clearInterval(checkInterval);
                                this._show_error(_t("Payment timeout. Please try again"));
                                line.set_payment_status('force_done');
                                resolve(false);
                            }
                            break;
                    }
                } catch (error) {
                    console.error('Status check error:', error);
                    if (attempts >= maxAttempts) {
                        clearInterval(checkInterval);
                        this._show_error(_t("Payment status check failed"));
                        if (this._isValidPaymentLine(line)) {
                            line.set_payment_status('force_done');
                        }
                        resolve(false);
                    }
                }
            };

            const checkInterval = setInterval(checkStatus, interval);
            // Initial check
            checkStatus();
        });
    }

    async _check_receipt_status() {
        if (!this.receiptUrl) {
            return 'error';
        }

        try {
            // Call backend to fetch receipt URL status
            const response = await this.env.services.orm.silent.call(
                "pos.payment.method",
                "check_moneris_receipt_status",
                [[this.payment_method.id], this.receiptUrl]
            );

            if (!response || response.error) {
                return 'pending';
            }

            console.log('Receipt URL response:', response);

            // Parse the receipt URL response
            const receiptData = response.receipt;
            if (!receiptData) {
                return 'pending';
            }

            // Check the actual transaction response inside data.response[0]
            const transactionResponse = receiptData.data?.response?.[0];
            if (transactionResponse) {
                const statusCode = transactionResponse.statusCode;
                const completed = transactionResponse.completed === "true";

                console.log('Receipt transaction status:', { statusCode, completed });

                // Approved status (5207 with completed=true)
                if (statusCode === "5207" && completed) {
                    return 'approved';
                }

                // Declined or not completed statuses
                if (["5206", "5453"].includes(statusCode)) {
                    return 'declined';
                }
            }

            // Check top-level status as fallback
            if (receiptData.statusCode === "5207" && receiptData.Completed === "true") {
                return 'approved';
            }

            return 'pending';

        } catch (error) {
            console.error('Error checking receipt status:', error);
            return 'error';
        }
    }

    _isValidPaymentLine(line) {
        const order = this.pos.get_order();
        if (!order || order.uid !== this.currentOrderUid) {
            return false;
        }

        return order.paymentlines.includes(line);
    }

    _storeTransactionDetails(line, response) {
        const transactionResponse = response.receipt?.data?.response?.[0];
        if (transactionResponse) {
            line.transaction_id = transactionResponse.transactionId || transactionResponse.cloudTicket || '';
            line.card_type = transactionResponse.cardType || '';
            line.auth_code = transactionResponse.authCode || '';
            line.cardholder_name = transactionResponse.cardName || '';

            if (transactionResponse.maskedPan) {
                line.card_number = transactionResponse.maskedPan;
            }

            // Store additional details for reference
            line.moneris_response_code = transactionResponse.responseCode;
            line.moneris_iso_code = transactionResponse.iso;
            line.moneris_reference = transactionResponse.realTimeUniqueId;
        }
    }

    async _storeTransactionDetailsFromPolling(line) {
        try {
            const response = await this.env.services.orm.silent.call(
                "pos.payment.method",
                "get_latest_moneris_status",
                [[this.payment_method.id]]
            );

            if (response && response.receipt) {
                const transactionResponse = response.receipt.data?.response?.[0];
                if (transactionResponse) {
                    line.transaction_id = transactionResponse.transactionId || transactionResponse.cloudTicket || '';
                    line.card_type = transactionResponse.cardType || '';
                    line.auth_code = transactionResponse.authCode || '';
                    line.cardholder_name = transactionResponse.cardName || '';

                    if (transactionResponse.maskedPan) {
                        line.card_number = transactionResponse.maskedPan;
                    }

                    line.moneris_response_code = transactionResponse.responseCode;
                    line.moneris_iso_code = transactionResponse.iso;
                    line.moneris_reference = transactionResponse.realTimeUniqueId;
                }
            }
        } catch (error) {
            console.error('Error storing transaction details from polling:', error);
        }
    }

    _startPolling() {
        // Poll every 2 seconds for payment status updates
        this.pollingInterval = setInterval(() => {
            this.handleMonerisStatusResponse();
        }, 2000);
    }

    async handleMonerisStatusResponse() {
        // This method can be called from outside for manual status checks
        try {
            const status = await this._check_receipt_status();
            const line = this.pending_moneris_line();

            if (!line) return false;

            switch (status) {
                case 'approved':
                    line.set_payment_status('done');
                    await this._storeTransactionDetailsFromPolling(line);
                    if (this.paymentNotificationResolver) {
                        this.paymentNotificationResolver(true);
                    }
                    return true;

                case 'declined':
                case 'failed':
                    this._show_error(_t("Payment was declined or failed"));
                    line.set_payment_status('force_done');
                    if (this.paymentNotificationResolver) {
                        this.paymentNotificationResolver(false);
                    }
                    return false;
            }

            return false;

        } catch (error) {
            console.error('Error in status response handler:', error);
            return false;
        }
    }

    pending_moneris_line() {
        const order = this.pos.get_order();
        if (!order || order.uid !== this.currentOrderUid) {
            return null;
        }

        // Find the first Moneris payment line that's waiting
        return order.paymentlines.find(line =>
            line.payment_method_id === this.payment_method.id &&
            ['waitingCapture', 'waitingCard'].includes(line.payment_status)
        );
    }

    _show_error(msg) {
        this.env.services.dialog.add(AlertDialog, {
            title: _t("Moneris Error"),
            body: msg,
        });
    }

    _showMsg(msg, title) {
        this.env.services.dialog.add(AlertDialog, {
            title: title || _t("Moneris"),
            body: msg,
        });
    }

    // Method to manually sync terminal (can be called from UI)
    async syncTerminal() {
        const result = await this._syncTerminal();
        if (result) {
            this.isTerminalSynced = true;
        }
        return result;
    }
}
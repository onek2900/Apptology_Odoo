/** @odoo-module */

import { PaymentInterface } from "@point_of_sale/app/payment/payment_interface";

export class PaymentNearPay extends PaymentInterface {

    send_payment_request(cid) {
        return new Promise((resolve, reject) => {
            const order = this.pos.get_order()
            const line = order.get_paymentline(cid);
            if (!line) {
                reject(new Error('Paymentline not found'));
                return;
            }
            // Simulate payment processing
            this._simulatePaymentProcess(line)
                .then((result) => {
                    line.card_type = 'NRP';
                    line.transaction_id = result.transactionId;
                    line.set_payment_status('retry');
                    console.log(`nearpay:${line.name}:${line.amount}:${order.name}`)
                    resolve(false);
                })
                .catch((error) => {
                    line.set_payment_status('retry');
                    reject(error);
                });
        });
    }

    send_payment_cancel(order, cid) {
        return new Promise((resolve) => {
            const line = order.get_paymentline(cid);
            if (line) {
                line.set_payment_status('cancelled');
            }
            resolve(true);
        });
    }

    close() {
        // Clean up any pending operations
    }

    // Helper methods for payment simulation
    _simulatePaymentProcess(line) {
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve({
                    success: true,
                    transactionId: 'NP' + Math.random().toString(36).substr(2, 9),
                    approvalCode: Math.random().toString(36).substr(2, 6).toUpperCase()
                });
            }, 500); // 500 milli second delay
        });
    }
}

// Register the payment method
import { register_payment_method } from "@point_of_sale/app/store/pos_store";
register_payment_method('NRP', PaymentNearPay);
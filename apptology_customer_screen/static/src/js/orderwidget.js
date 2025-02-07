/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { onWillUpdateProps, onMounted } from "@odoo/owl";
import { OrderWidget } from "@point_of_sale/app/generic_components/order_widget/order_widget";
import { useService } from "@web/core/utils/hooks";

/**
 * Patch for OrderWidget to handle order line updates and bus communication
 * @patch {OrderWidget}
 */
patch(OrderWidget.prototype, {
    /**
     * Sets up the component with bus communication and lifecycle hooks
     * @setup
     */
    setup() {
        this.orm = useService("orm");
        /**
         * Processes order lines into a standardized format
         * @param {Object} lines - Raw order lines from props
         * @returns {Array} Processed order lines with required fields
         */
        const processLines = (lines = {}) => {
            try {
                return Object.values(lines).map(item => ({
                    currency_symbol:item.pos.currency.symbol,
                    product_id: item.product.id,
                    product_name: item.full_product_name,
                    order_name: item.order.name,
                    price: item.price,
                    quantity: item.quantity,
                    discount: item.discount,
                    tax_ids: item.product.taxes_id
                }));
            } catch (error) {
                console.warn('Error processing lines:', error);
                return [];
            }
        };

        onMounted(() => this.triggerBus(processLines(this.props?.lines)));

        onWillUpdateProps((nextProps) => this.triggerBus(processLines(nextProps?.lines)));
    },

    /**
     * Triggers bus event with order details
     * @param {Array} data - Processed order lines to send
     * @returns {Promise} Result of bus communication
     */
    async triggerBus(data) {
        await this.orm.call("pos.order", "trigger_bus", [[]], { order_details: data });
    }
});
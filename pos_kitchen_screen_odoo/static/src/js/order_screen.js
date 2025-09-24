/** @odoo-module */

import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";
const {DateTime} = luxon;
import { Component, onWillStart, useState, onMounted, onWillUnmount, whenReady, App } from "@odoo/owl";
import { makeEnv, startServices } from "@web/env";
import { templates } from "@web/core/assets";
import { _t } from "@web/core/l10n/translation";
import { session } from "@web/session";


// Constants for order statuses
const ORDER_STATUSES = {
    DRAFT: 'draft',
    WAITING: 'waiting',
    READY: 'ready',
    CANCEL: 'cancel'
};

// Constants for bus events
const BUS_CHANNEL = "pos_order_created";
const BUS_EVENT = {
    MESSAGE: "pos_order_created",
    MODEL: "pos.order"
};

/**
 * Custom hook for order management functionality
 * @param {Object} rpc - RPC service
 * @param {number} screenId - Shop ID
 * @returns {Object} Order management methods
 */
const useOrderManagement = (rpc, screenId) => {

    /**
     * Fetch order details from server
     * @returns {Promise<Object>} Order details and counts
     */
    const fetchOrderDetails = async () => {
        try {
            const result = await rpc("/pos.order/get_order_details", {
                screen_id: screenId
            });
            return {
                order_details: result.orders,
            };
        } catch (error) {
            console.error("Error fetching order details:", error);
            return {
                order_details: [],
            };
        }
    };

    return {
        fetchOrderDetails,
    };
};

/**
 * Kitchen Dashboard Component
 */
export class OrderScreenDashboard extends Component {
    /**
     * Component setup
     */
    setup() {
        this.initializeServices();
        this.initializeState();
        this.setupEventListeners();

        onWillUnmount(() => {
            if (this.refreshInterval) {
                clearInterval(this.refreshInterval);
            }
            this.busService.removeEventListener('notification', this.handleNotification);
        })
    }

    /**
     * Initialize required services
     */
    initializeServices() {
        this.busService = this.env.services.bus_service;
        this.orm = this.env.services.orm;
        this.rpc = this.env.services.rpc;
        this.user = this.env.services.user;
        this.notification = this.env.services.notification;
    }

    /**
     * Initialize component state
     */
    initializeState() {
        const screenId = this.getScreenId();

        this.state = useState({});

        this.orderManagement = useOrderManagement(this.rpc, screenId);
    }

    /**
     * Get screenId from context or session storage
     * @returns {number} screenId
     */
    getScreenId() {
        const screenId = odoo.kitchen_screen;
        if (screenId) {
            sessionStorage.setItem('screen_id', screenId);
            return screenId;
        }
        return parseInt(sessionStorage.getItem('screen_id'), 10);
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        this.busService.addChannel(BUS_CHANNEL);

        onWillStart(async () => {
            this.busService.addEventListener('notification', this.handleNotification.bind(this));
            await this.refreshOrderDetails();
        });

        onMounted(() => {
            this.startAutoRefresh();
        });
    }

    /**
     * Start auto-refresh timer
     */
    startAutoRefresh() {
        // Refresh every 5 seconds
        this.refreshInterval = setInterval(() => {
            this.refreshOrderDetails();
        }, 5000);
    }

    /**
     * Handle bus notifications
     * @param {Object} message - Notification message
     */
    async handleNotification(message) {
        const payload = message.detail[0].payload;
        if (payload.message === BUS_EVENT.MESSAGE &&
            payload.res_model === BUS_EVENT.MODEL) {
            await this.refreshOrderDetails();
        }
    }

    /**
     * Refresh order details
     */
    async refreshOrderDetails() {
        try {
            this.state.loading = true;
            this.state.error = null;
            const details = await this.orderManagement.fetchOrderDetails();
            Object.assign(this.state, details);
        } catch (error) {
            this.state.error = "Failed to refresh orders";
            this.notification.add("Failed to refresh orders", {
                title: "Error",
                type: "danger"
            });
        } finally {
            this.state.loading = false;
        }
    }

    get noOrders() {
        return _t("No orders !");
    }

    get orderInProgress() {
        return this.state.order_details.filter(o =>
            o.order_status === 'draft')
    }

    get orderCompleted() {
        const userTimezone = this.user.tz || 'UTC';
        return this.state.order_details.filter(o => {
            // Ensure write_date is in a format Luxon can parse (e.g., "2024-11-12T09:00:46")
            const formattedWriteDate = o.write_date.replace(' ', 'T');

            // Parse the formatted date string in UTC and convert to user timezone
            const writeDate = DateTime.fromISO(formattedWriteDate, {zone: 'UTC'})
                .setZone(userTimezone);

            return (
                o.order_status === 'ready' &&
                writeDate > DateTime.now().minus({hours: 6}) // Completed within the last hour
            );
        });
    }
}

OrderScreenDashboard.template = 'pos_kitchen_screen_odoo.OrderScreenDashboard';

export async function createOrderApp() {
    await whenReady();
    const appEnv = makeEnv();
    await startServices(appEnv);
    const app = new App(OrderScreenDashboard, {
        templates,
        env: appEnv,
        dev: appEnv.debug,
        translateFn: _t,
        translatableAttributes: ["data-tooltip"],
    });
    return app.mount(document.body);
}

/** @odoo-module */

import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";
const {DateTime} = luxon;
import { Component, onWillStart, useState, onMounted, onWillUnmount, whenReady, App } from "@odoo/owl";
import { makeEnv, startServices } from "@web/env";
import { templates } from "@web/core/assets";
import { _t } from "@web/core/l10n/translation";
import { session } from "@web/session";

/**
 * Customer Dashboard Component
 */
export class CustomerScreenDashboard extends Component {
    /**
     * Component setup
     */
    setup() {
        this.busService = this.env.services.bus_service;
        this.state = useState({
            orders: [],
            order_name:"",
            total_amount:"",
            currency_symbol:""
        });
        this.channel="test_channel_first";
        this.busService.addChannel("test_channel_first");
        this.busService.addEventListener('notification', ({detail: notifications})=>{
            notifications = notifications.filter(item => item.payload.channel === this.channel)
            notifications.forEach(item => {
                this.state.orders = item.payload.orders;
                this.state.order_name=item.payload.order_name;
                this.state.total_amount=item.payload.total_amount;
                this.state.currency_symbol=item.payload.currency_symbol;
            })
        });
    }
}

// Component registration
CustomerScreenDashboard.template = 'CustomerScreenDashboard';
registry.category("actions").add("customer_screen_dashboard_tags", CustomerScreenDashboard);


export async function customerScreenApp() {
    await whenReady();
    const appEnv = makeEnv();
    await startServices(appEnv);
    const app = new App(CustomerScreenDashboard, {
        templates,
        env: appEnv,
        dev: appEnv.debug,
        translateFn: _t,
        translatableAttributes: ["data-tooltip"],
    });
    return app.mount(document.body);
}
/** @odoo-module */
 import { createKitchenApp } from "./kitchen_screen"
 import { createOrderApp } from "./order_screen"

if (odoo.screen === "order") {
    createOrderApp()
} else if (odoo.screen === "kitchen") {
    createKitchenApp()
}
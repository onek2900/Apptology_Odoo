/** @odoo-module */
 import { customerScreenApp } from "./custom_screen"

if (odoo.screen === "customer") {
    customerScreenApp()
}
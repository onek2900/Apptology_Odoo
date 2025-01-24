/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";


export class BrowsingComponent extends Component {


}

BrowsingComponent.template = "apptology_browsing.BrowsingComponent";

registry.category("actions").add("browse_apptology", BrowsingComponent);
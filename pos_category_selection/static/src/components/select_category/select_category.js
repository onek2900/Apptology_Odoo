/** @odoo-module */

import { Component } from "@odoo/owl";

/**
 * @typedef {Object} Category
 * @property {number} id
 * @property {string?} name
 * @property {string?} imageUrl
 */
export class SelectCategory extends Component {
    static template = "pos_category_selection.SelectCategory";
    static props = {
        categories: {
            type: Array,
            element: Object,
            shape: {
                id: Number,
                name: { type: String, optional: true },
                imageUrl: { type: [String, Boolean], optional: true },
            },
        },
        onClick: { type: Function },
    };

}

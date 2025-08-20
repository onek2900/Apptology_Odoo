/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { Order, Orderline } from "@point_of_sale/app/store/models";

patch(Order.prototype, {
    setup(_defaultObj, options) {
        super.setup(...arguments);
        this.l10n_fr_hash = this.l10n_fr_hash || false;
        // this.save_to_db();
    },
    get_orderline_by_id(id) {
        var result = []
        for(let line of this.get_orderlines()){
            if (line.id == id) {
                result.push(line)
            }
        }
        return result
    },
    async set_orderline_options(orderline, options) {
        for(let all_orderline of this.get_orderlines()){
            if (all_orderline.add_section) {
                orderline.set_ref_label(all_orderline.add_section)
            }
        }
        super.set_orderline_options(orderline, options);
    }
});

patch(Orderline.prototype, {
    setup(_defaultObj, options) {
        super.setup(...arguments);
        this.is_sh_order_label_demo_product = this.product.sh_order_label_demo_product
    },
    init_from_JSON(json) {
        super.init_from_JSON(...arguments);
        if (json && (json.add_section || json.ref_label)) {
            this.add_section = json.add_section;
            this.ref_label = json.ref_label;
        } else {
            this.add_section = '';
            this.ref_label = '';
        }
    },
    set_orderline_label(value) {
        this.add_section = value
    },
    get_orderline_label() {
        return this.add_section
    },
    set_ref_label(value) {
        this.ref_label = value
    },
    get_ref_label() {
        return this.ref_label
    },
    getDisplayData() {
        var result = super.getDisplayData()
        result['is_sh_order_label_demo_product'] = this.is_sh_order_label_demo_product
        result['add_section'] = this.get_orderline_label()
        result['ref_label'] = this.get_ref_label()
        result['display_label_in_line'] = this.order && !this.order.finalized && this.pos.config.enable_order_line_label
        result['display_label_in_receipt'] = this.order && this.order.finalized && this.pos.config.enable_order_line_label_in_receipt
        return result
    },
    export_as_JSON() {
        var json = super.export_as_JSON(...arguments);
        json.add_section = this.add_section || null;
        return json
    },
});
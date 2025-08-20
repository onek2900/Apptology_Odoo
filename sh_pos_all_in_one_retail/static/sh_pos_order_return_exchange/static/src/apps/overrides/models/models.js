/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { Order, Orderline } from "@point_of_sale/app/store/models";
import { _t } from "@web/core/l10n/translation";

patch(Orderline.prototype, {
    setup(options) {
        super.setup(...arguments);
        // if ( !options.json ) {
        this.sh_sh_line_id = false
        // }
    },
    set_sh_line_id (sh_line_id) {
        this.sh_sh_line_id = sh_line_id;
    },
    set_old_sh_line_id (old_sh_line_id) {
        this.old_sh_line_id = old_sh_line_id;
    },
    export_as_JSON () {
        var json = super.export_as_JSON();
        json.sh_line_id = this.sh_line_id;
        json.old_sh_line_id = this.old_sh_line_id;
        return json;
    }
})

patch(Order.prototype, {
    setup(options) {
        super.setup(...arguments);
        // if ( !options.json ) {
        this.is_return_order = false
        // }
    },
    init_from_JSON(json) {
        super.init_from_JSON(...arguments);
        if ( json.is_return_order) {
            this.is_return_order = json.is_return_order;
        }
    },
    export_as_JSON() {
        const json = super.export_as_JSON(...arguments);
        if ( this.is_return_order ) {
            json.is_return_order = this.is_return_order;
            json.old_pos_reference = this.old_pos_reference;
        }
        if ( this.is_exchange_order ) {
            json.is_exchange_order = this.is_exchange_order;
            json.old_pos_reference = this.old_pos_reference;
        }

        return json;
    },
    async add_product (product, options) {
        var order = this.pos.get_order();
       let res = await super.add_product(product, options);
        if (options !== undefined) {
            if (options.sh_line_id) {
                order.selected_orderline.set_sh_line_id(options.sh_line_id);
                order.selected_orderline.set_old_sh_line_id(options.sh_line_id);
            }
        }
        return res
    }
})

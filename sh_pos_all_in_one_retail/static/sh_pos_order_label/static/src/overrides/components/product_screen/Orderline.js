/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { Orderline } from "@point_of_sale/app/generic_components/orderline/orderline";

import { _t } from "@web/core/l10n/translation";
import { usePos } from "@point_of_sale/app/store/pos_hook";

patch(Orderline.prototype, {
    async remove_label(lable) {
        event.stopPropagation()
        var self = this
        if (lable) {
            var res = self.get_label_line_by_name(lable)
        }
        if (res &&  this.env.services.pos.config.enabel_delete_label_with_product) {
            var remove = []
            var orderlines = this.env.services.pos.get_order().get_orderlines()
            for (let orderline of orderlines) {
                if (orderline) {
                    if (orderline['ref_label'] && res.add_section == orderline['ref_label']) {
                        remove.push(orderline)
                    } else {
                        if (orderline.add_section == '' && orderline.product.sh_order_label_demo_product) {
                            remove.push(orderline)
                        }
                    }
                }
            }
            for (var i = 0; i < remove.length; i++) {
                await this.env.services.pos.get_order().removeOrderline(remove[i])
            }

            await this.env.services.pos.get_order().removeOrderline(res)
        } else {
            await this.env.services.pos.get_order().removeOrderline(res)
        }
    },
    get_label_line_by_name(name) {
        var res = []
        var lines = this.env.services.pos.get_order().get_orderlines()
        for (let line of lines) {
            if (line.add_section == name) {
                res.push(line)
            }
        }
        return res[0]
    },

});

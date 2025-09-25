/** @odoo-module **/
/* global pagination */

import { OrderListScreen } from "@sh_pos_all_in_one_retail/static/sh_pos_order_list/apps/screen/order_list_screen/order_list_screen";
import { ReturnOrderPopup } from "@sh_pos_all_in_one_retail/static/sh_pos_order_return_exchange/apps/popups/return_order_popup/return_order_popup";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";


patch(OrderListScreen.prototype, {
    setup() {
        this.is_return_filter = false;
        super.setup()
        this.popup = useService("popup");
    },
    get_return_filter() {
        return this.is_return_filter;
    },
    apply_return_filter(data) {
        this.is_return_filter = data
    },
    async sh_return_pos_order(ev) {
        $(ev.target).toggleClass('highlight')
        this.apply_return_filter(!this.get_return_filter());
        this.offset = 0;
        this.fetch()
    },
    get allPosOrders() {
        const toUniqueSorted = (arr) => {
            const sorted = (arr || []).slice().sort((a, b) => {
                const aid = a && a[0] ? Number(a[0]['id']) : 0;
                const bid = b && b[0] ? Number(b[0]['id']) : 0;
                return bid - aid;
            });
            const seen = new Set();
            const out = [];
            for (const tpl of sorted) {
                const hid = tpl && tpl[0] ? tpl[0].id : null;
                if (!hid || seen.has(hid)) continue;
                seen.add(hid);
                out.push(tpl);
            }
            return out;
        };
        if (this.isSearch) {
            return toUniqueSorted(this.subFilterdOrders);
        } else {
            const orders = Object.values(this.pos.db.pos_order_by_id || {});
            if (this.get_return_filter()) {
                const filtered = orders.filter((x) => x && x[0] && x[0].is_return_order) || []
                return toUniqueSorted(filtered);
            } else {
                const filtered = orders.filter((x) => x && x[0] && !x[0].is_return_order) || []
                return toUniqueSorted(filtered.length ? filtered : orders);
            }
        }
    },
    clickLine(orderlist) {
        var order = orderlist[0]
        if ($('#inner_table_' + order.id) && $('#inner_table_' + order.id).hasClass('sh_hide_lines')) {
            $('.sh_sub_order_line').addClass('sh_hide_lines')
            $('#inner_table_' + order.id).removeClass('sh_hide_lines')
            $('.sh_order_line').removeClass('highlight')
            $(event.target).parent().toggleClass('highlight')
        } else {
            $('#inner_table_' + order.id).addClass('sh_hide_lines')
            $(event.target).parent().toggleClass('highlight')
        }
        $('#sh_order_reference_line' + order.id).toggleClass('sh_hide_lines') 
        this.render(true)
    },
    sh_appy_search(search) {
        var self = this;
        if (this.isSearch && (this.shFilteredOrders && this.shFilteredOrders.length)) {
            return this.shFilteredOrders.filter(function (template) {
                if (self.get_return_filter()){
                    if (template[0].name.indexOf(search) > -1 && template[0].is_return_order ) {
                        return true;
                    } else if (template[0]["pos_reference"].indexOf(search) > -1 && template[0].is_return_order) {
                        return true;
                    } else if (template[0]["partner_id"] && template[0]["partner_name"] && (template[0]["partner_name"].indexOf(search) > -1 || template[0]["partner_name"].toLowerCase().indexOf(search) > -1) && template[0].is_return_order) {
                        return true;
                    } else if (template[0]["state"] && template[0]["state"].indexOf(search) > -1 && template[0].is_return_order ) {
                        return true;
                    } else if (template[0]["date_order"] && template[0]["date_order"].indexOf(search) > -1 && template[0].is_return_order) {
                        return true;
                    } else {
                        return false;
                    }
                }else{
                    if (template[0].name.indexOf(search) > -1 && !self.get_return_filter() && !template[0].is_return_order ) {
                        return true;
                    } else if (template[0]["pos_reference"].indexOf(search) > -1 && !self.get_return_filter() && !template[0].is_return_order) {
                        return true;
                    } else if (template[0]["partner_id"] && template[0]["partner_name"] && (template[0]["partner_name"].indexOf(search) > -1 || template[0]["partner_name"].toLowerCase().indexOf(search) > -1) && !self.get_return_filter() && !template[0].is_return_order) {
                        return true;
                    } else if (template[0]["state"] && template[0]["state"].indexOf(search) > -1 && !self.get_return_filter() && !template[0].is_return_order) {
                        return true;
                    } else if (template[0]["date_order"] && template[0]["date_order"].indexOf(search) > -1 && !self.get_return_filter() && !template[0].is_return_order) {
                        return true;
                    } else {
                        return false;
                    }
                }
            })
        } else {
            return Object.values(this.pos.db.pos_order_by_id).filter(function (template) {
                if (self.get_return_filter()){
                    if (template[0].name.indexOf(search) > -1 && template[0].is_return_order ) {
                        return true;
                    } else if (template[0]["pos_reference"].indexOf(search) > -1 && template[0].is_return_order) {
                        return true;
                    } else if (template[0]["partner_id"] && template[0]["partner_name"] && (template[0]["partner_name"].indexOf(search) > -1 || template[0]["partner_name"].toLowerCase().indexOf(search) > -1) && template[0].is_return_order) {
                        return true;
                    } else if (template[0]["state"] && template[0]["state"].indexOf(search) > -1 && template[0].is_return_order ) {
                        return true;
                    } else if (template[0]["date_order"] && template[0]["date_order"].indexOf(search) > -1 && template[0].is_return_order) {
                        return true;
                    } else {
                        return false;
                    }
                }else{
                    if (template[0].name.indexOf(search) > -1 && !self.get_return_filter() && !template[0].is_return_order ) {
                        return true;
                    } else if (template[0]["pos_reference"].indexOf(search) > -1 && !self.get_return_filter() && !template[0].is_return_order) {
                        return true;
                    } else if (template[0]["partner_id"] && template[0]["partner_name"] && (template[0]["partner_name"].indexOf(search) > -1 || template[0]["partner_name"].toLowerCase().indexOf(search) > -1) && !self.get_return_filter() && !template[0].is_return_order) {
                        return true;
                    } else if (template[0]["state"] && template[0]["state"].indexOf(search) > -1 && !self.get_return_filter() && !template[0].is_return_order) {
                        return true;
                    } else if (template[0]["date_order"] && template[0]["date_order"].indexOf(search) > -1 && !self.get_return_filter() && !template[0].is_return_order) {
                        return true;
                    } else {
                        return false;
                    }
                }
            })
        }
    },
    async exchange_pos_order(ev) {
        var self = this;
        ev.stopPropagation();
        var order_id = $(ev.target).attr('data-id')
        var order = self.pos.db.pos_order_by_id[order_id]


        const { confirmed } = await this.popup.add(ReturnOrderPopup, {
            title: _t("Exchange"),
            'order': order[0],
            'lines': order[1],
            'sh_return_order': false,
            'exchange_order': true,
            'from_barcode': true
        });


    },
    async return_pos_order(ev) {
        var self = this;
        ev.stopPropagation();
        var order_id = $(ev.target).attr('data-id')
        var order = self.pos.db.pos_order_by_id[order_id]

        const { confirmed } = await this.popup.add(ReturnOrderPopup, {
            title: _t("Return"),
            'order': order[0],
            'lines': order[1],
            'sh_return_order': true,
            'exchange_order': false,
            'from_barcode': true
        });

    }
})

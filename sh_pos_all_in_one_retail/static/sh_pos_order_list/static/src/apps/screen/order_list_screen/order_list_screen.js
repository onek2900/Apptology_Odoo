/** @odoo-module **/
/* global pagination */

import { registry } from "@web/core/registry";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { onMounted } from "@odoo/owl";
import { Order, Orderline } from "@point_of_sale/app/store/models";

import { Component, onWillUnmount, useRef, useState } from "@odoo/owl";

export class OrderListScreen extends Component {
    static template = "sh_pos_order_list.OrderListScreen";
    setup() {
        this.pos = usePos();
        this.ui = useState(useService("ui"));
        this.isSearch = false;
        this.currentPage = 1;
        this.totalCount = this.allPosOrders.length;
        this.nPerPage = this.pos.config.sh_how_many_order_per_page;
        this.offset = this.nPerPage + (this.currentPage - 1) * this.nPerPage
        this.limit = 0
        this.ordersToShow = this.allPosOrders.slice(0, this.offset);
        // use if the filter is alrady apply and than apply state filter
        this.shFilteredOrders = []
        // sub filter order
        this.subFilterdOrders = []
        onMounted(this.onMounted);
    }
    onMounted() {
        var self = this;
    }
    get currentOrder() {
        if (this.pos.get_order()) {
            return this.pos.get_order()
        } else {
            return false
        }
    }
    async print_pos_order(event) {
        var self = this;
        event.stopPropagation()
        var order_id = $(event.target).attr('data-id')
        var order = self.pos.db.pos_order_by_id[order_id]

        if ( order ) {
            var newOrder = await new Order(
                { env: self.env },
                {
                    pos: self.pos,
                    temporary: true,
                }
            );
            if (order[0]) {
                newOrder.name = order[0].pos_reference
                newOrder.trackingNumber = order[0].trackingNumber
            }
            if (order[1]) {
                for (let line of order[1]) {
                    var product = self.pos.db.get_product_by_id(line.product_id);
                    const newline = await new Orderline(
                        { env: this.env },
                        { pos: self.pos, order: newOrder, product: product, quantity: line.qty }
                    );
                    newOrder.orderlines.push(newline)
                }
            }

            this.pos.showScreen("ShReceiptScreen", {
                'order': newOrder,
                'selected_order': order[0]
            });
        }
    }
    reorder_pos_order(event) {
        var self = this;
        event.stopPropagation()
        var order_id = $(event.target).attr('data-id')
        var order = self.pos.db.pos_order_by_id[order_id]
        if (order) {
            var order_lines = self.pos.get_order().get_orderlines();
            [...order_lines].map(async (line) => await self.currentOrder.removeOrderline(line));
            if (order[1]) {
                for (let line of order[1]) {
                    var product = self.pos.db.get_product_by_id(line.product_id);
                    if (product) {
                        self.currentOrder.add_product(product, {
                            quantity: line.qty,
                            price: line.price_unit,
                            discount: line.discount,
                            customerNote: line.customer_note || null,
                            extras: {
                                add_section: line.add_section ? line.add_section : '',
                            },
                        });
                    }
                }
                self.back()
            }
        }
    }
    sh_appy_search(search) {
        if (this.isSearch && (this.shFilteredOrders && this.shFilteredOrders.length)) {
            return this.shFilteredOrders.filter(function (template) {
                if (template[0].name.indexOf(search) > -1) {
                    return true;
                } else if (template[0]["pos_reference"].indexOf(search) > -1) {
                    return true;
                } else if (template[0]["partner_id"] && template[0]["partner_name"] && (template[0]["partner_name"].indexOf(search) > -1 || template[0]["partner_name"].toLowerCase().indexOf(search) > -1)) {
                    return true;
                } else if (template[0]["state"] && template[0]["state"].indexOf(search) > -1) {
                    return true;
                } else if (template[0]["date_order"] && template[0]["date_order"].indexOf(search) > -1) {
                    return true;
                } else {
                    return false;
                }
            })
        } else {
            return Object.values(this.pos.db.pos_order_by_id).filter(function (template) {
                if (template[0].name.indexOf(search) > -1) {
                    return true;
                } else if (template[0]["pos_reference"].indexOf(search) > -1) {
                    return true;
                } else if (template[0]["partner_id"] && template[0]["partner_name"] && (template[0]["partner_name"].indexOf(search) > -1 || template[0]["partner_name"].toLowerCase().indexOf(search) > -1)) {
                    return true;
                } else if (template[0]["state"] && template[0]["state"].indexOf(search) > -1) {
                    return true;
                } else if (template[0]["date_order"] && template[0]["date_order"].indexOf(search) > -1) {
                    return true;
                } else {
                    return false;
                }
            })
        }
    }
    async updateOrderList(event) {
        var search = event.target.value;
        if (search) {
            this.isSearch = true
            var Orders = await this.sh_appy_search(search)
            if (Orders && Orders.length) {
                this.shFilteredOrders = Orders
                this.subFilterdOrders = Orders
                this.offset = 0;
                this.fetch()
            } else {
                this.shFilteredOrders = []
                this.subFilterdOrders = []
                this.offset = 0;
                this.fetch()
            }
        } else {
            this.isSearch = false
            this.subFilterdOrders = []
            this.shFilteredOrders = []
            this.offset = 0;
            this.fetch()
        }
    }
    async change_date(event) {
        let search = event.target.value;
        this.isSearch = true
        this.shFilteredOrders = []
        this.subFilterdOrders = []
        var Orders = await this.sh_appy_search(search)
        if (Orders && Orders.length) {
            this.shFilteredOrders = Orders
            this.subFilterdOrders = Orders
            this.offset = 0;
            this.fetch()
        } else {
            this.shFilteredOrders = []
            this.subFilterdOrders = []
            this.offset = 0;
            this.fetch()
        }
    }
    async ShApplyFilter(ev) {
        let search = ev.target.value;
        if (search == "all") {
            this.isSearch = false
            if (this.shFilteredOrders && this.shFilteredOrders.length) {
                this.isSearch = true
            } else {
                this.subFilterdOrders = []
            }
            this.offset = 0;
            this.fetch()
        } else {
            this.isSearch = true
            var Orders = await this.sh_appy_search(search)
            if (Orders && Orders.length) {
                this.subFilterdOrders = Orders
                this.offset = 0;
                this.fetch()
            } else {
                this.shFilteredOrders = []
                this.subFilterdOrders = []
                this.offset = 0;
                this.fetch()
            }
        }
    }
    async fetch() {
        // Show orders from the backend.
        this.limit = this.offset;
        this.offset = this.nPerPage + (this.currentPage - 1) * this.nPerPage;
        this.ordersToShow = await this.allPosOrders.slice(this.limit, this.offset);
        this.render(true)
    }
    get allPosOrders() {
        // Source array
        const arr = this.isSearch ? (this.subFilterdOrders || []) : Object.values(this.pos.db.pos_order_by_id || {});
        // Sort newest first
        const sorted = arr.slice().sort((a, b) => {
            const aid = a && a[0] ? Number(a[0]['id']) : 0;
            const bid = b && b[0] ? Number(b[0]['id']) : 0;
            return bid - aid;
        });
        // De-duplicate by order header id to avoid doubles when sources overlap
        const unique = [];
        const seen = new Set();
        for (const tpl of sorted) {
            const hid = tpl && tpl[0] ? tpl[0].id : null;
            if (!hid) continue;
            if (seen.has(hid)) continue;
            seen.add(hid);
            unique.push(tpl);
        }
        return unique;
    }
    onNextPage() {
        if (this.currentPage <= this.lastPage) {
            this.currentPage += 1;
            this.fetch()
        }
    }
    onPrevPage() {
        if (this.currentPage - 1 > 0) {
            this.currentPage -= 1;
            this.limit = this.offset;
            this.offset = this.nPerPage + (this.currentPage - 1 - 1) * this.nPerPage;
            this.fetch()
        }
    }
    get lastPage() {
        let nItems = 0
        if (this.isSearch) {
            nItems = this.allPosOrders.length;
            return Math.trunc(nItems / (this.nPerPage + 1));
        } else {
            nItems = this.totalCount;
            return Math.trunc(nItems / (this.nPerPage + 1));
        }
    }
    get pageNumber() {
        const currentPage = this.currentPage;
        const lastPage = this.lastPage + 1;
        return isNaN(lastPage) ? "" : `(${currentPage}/${lastPage})`;
    }
    clear_search() {
        this.isSearch = false
        $('.sh_pos_order_search').val('')
        $('#date1').val('')
        this.subFilterdOrders = []
        this.shFilteredOrders = []
        this.offset = this.nPerPage + (this.currentPage - 1 - 1) * this.nPerPage;
        this.fetch()
    }
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
        this.render(true)
    }
    back() {
        this.pos.showScreen('ProductScreen')
    }
}
registry.category("pos_screens").add("OrderListScreen", OrderListScreen);

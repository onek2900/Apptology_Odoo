/** @odoo-module */
import { patch } from "@web/core/utils/patch";
import { ActionpadWidget } from "@point_of_sale/app/screens/product_screen/action_pad/action_pad";
import { useService } from "@web/core/utils/hooks";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { _t } from "@web/core/l10n/translation";


/**
 * @props partner
 */

// Keep a reference to any existing setup so we can chain correctly
const PreviousSetup_OrderButton = ActionpadWidget.prototype.setup;

patch(ActionpadWidget.prototype, {
    setup(...args) {
        if (typeof PreviousSetup_OrderButton === "function") {
            PreviousSetup_OrderButton.apply(this, args);
        }
        // Ensure POS and UI services are available (defensive guards)
        this.pos = this.pos || this.env?.services?.pos;
        this.ui = this.ui || this.env?.services?.ui;
        this.orm = useService("orm");
        this.rpc = useService("rpc");
        this.popup = useService("popup");
    },
    get swapButton() {
        return (
            this.props?.actionType === "payment" &&
            this.pos?.config?.module_pos_restaurant
        );
    },
    get currentOrder() {
        return this.pos.get_order();
    },
    get swapButtonClasses() {
        return {
            "highlight btn-primary": this.currentOrder?.hasChangesToPrint(),
            altlight:
                !this.currentOrder?.hasChangesToPrint() && this.currentOrder?.hasSkippedChanges(),
        };
    },

    async submitOrder() {
        var line = []
        var self = this;
        if (!this.clicked) {
            this.clicked = true;
            try {
                var order_name=this.pos.selectedOrder.name
                await this.orm.call("pos.order", "check_order_status", ["", order_name]).then(function(result){
                    if (result==false){
                    self.kitchen_order_status=false
                         self.popup.add(ErrorPopup, {
                        title: _t("Order is Completed"),
                        body: _t("There Order is Completed please create a new Order"),
                    });
                    }
                    else{
                        self.kitchen_order_status=true
                    }
                });
                if ( self.kitchen_order_status){
                    const ticketUid = 'ticket_' + Date.now() + '_' + Math.floor(Math.random()*1000);
                    const changeSummary = this.currentOrder.getOrderChanges ? this.currentOrder.getOrderChanges() : null;
                    const newLineSummary = [];
                    if (changeSummary && changeSummary.orderlines) {
                        for (const change of Object.values(changeSummary.orderlines)) {
                            const deltaQty = Number(change.quantity) || 0;
                            if (deltaQty > 0) {
                                const productData = this.pos?.db?.product_by_id?.[change.product_id];
                                newLineSummary.push({
                                    product_id: change.product_id,
                                    product_name: productData?.display_name || change.name || '',
                                    quantity: deltaQty,
                                    note: change.note || '',
                                    ticket_uid: ticketUid,
                                    // Hint for kitchen: whether this is a modifier/topping
                                    is_topping: Boolean(productData?.is_topping ?? productData?.sh_is_topping ?? false),
                                });
                            }
                        }
                    }
                    await this.pos.sendOrderInPreparationUpdateLastChange(this.currentOrder);
                    const currentOrder = this.currentOrder;
                    // Persist only lines that do not yet have a kitchen_ticket_uid assigned
                    for (const ol of currentOrder.orderlines) {
                        if (!ol.product) continue;
                        // Skip lines already sent in a previous press
                        if (ol.kitchen_ticket_uid) continue;
                        const product = ol.product;
                        const taxes = typeof ol.get_taxes === 'function' ? ol.get_taxes() : [];
                        const taxIds = taxes.map((tax) => tax.id);
                        const prices = typeof ol.get_all_prices === 'function' ? ol.get_all_prices() : {};
                        const productIsTopping = Boolean(product.is_topping ?? product.sh_is_topping);
                        const payload = {
                            qty: ol.quantity,
                            price_unit: ol.price,
                            price_subtotal: prices.priceWithoutTax ?? ol.quantity * ol.price,
                            price_subtotal_incl: prices.priceWithTax ?? ol.get_display_price(),
                            discount: ol.discount,
                            product_id: product.id,
                            tax_ids: [[6, 0, taxIds]],
                            pack_lot_ids: [],
                            full_product_name: product.display_name,
                            price_extra: ol.price_extra,
                            is_cooking: true,
                            note: ol.customerNote,
                            sh_is_topping: productIsTopping,
                            product_sh_is_topping: Boolean(product.sh_is_topping),
                            kitchen_ticket_uid: ticketUid,
                        };
                        line.push([0, 0, payload]);
                        // Mark this line as assigned to this ticket so we don't resend it on next presses
                        try { ol.kitchen_ticket_uid = ticketUid; } catch (_) {}
                    }
                    var orders = [{
                        'pos_reference': this.pos.get_order().name,
                        'ticket_uid': ticketUid,
                        'kitchen_new_lines': newLineSummary,
                        'amount_total': 0,
                        'amount_paid': 0,
                        'amount_return': '0',
                        'amount_tax': 2.18,
                        'lines': line,
                        'is_cooking': true,
                        'order_status': 'draft',
                        'company_id': this.pos.company.id,
                        'session_id': (currentOrder && currentOrder.pos_session_id),
                        'hour': ((currentOrder && currentOrder.date_order && currentOrder.date_order.c && currentOrder.date_order.c.hour) || new Date().getHours()),
                        'minutes': ((currentOrder && currentOrder.date_order && currentOrder.date_order.c && currentOrder.date_order.c.minute) || new Date().getMinutes()),
                        'table_id': ((currentOrder && currentOrder.pos && currentOrder.pos.table && currentOrder.pos.table.id) || false),
                        'floor': ((currentOrder && currentOrder.pos && currentOrder.pos.currentFloor && currentOrder.pos.currentFloor.name) || 'Pickup'),
                        'config_id': ((currentOrder && currentOrder.pos && currentOrder.pos.config && currentOrder.pos.config.id) || (this.pos && this.pos.config && this.pos.config.id))
                    }]
                    // Fire-and-forget bus push so kitchen screen updates immediately without polling
                    try {
                        const current = this.currentOrder;
                        const meta = {
                            partner: current?.get_partner()?.name || '',
                            table_id: (current?.pos?.table && [current.pos.table.id, current.pos.table.name]) || null,
                            floor: (current?.pos?.currentFloor && current.pos.currentFloor.name) || '',
                            is_online_order: Boolean(current?.is_online_order),
                            order_type: current?.order_type || '',
                        };
                        await this.rpc('/pos/kitchen/push_delta', {
                            shop_id: this.pos.config.id,
                            order_ref: this.pos.get_order().name,
                            ticket_uid: ticketUid,
                            new_lines: newLineSummary,
                            meta,
                        });
                    } catch (e) { /* ignore client-side bus failures */ }

                    // Persist order + lines so fetch includes sent-but-unpaid orders
                    await self.orm.call("pos.order", "get_details", ["", self.pos.config.id, orders])
                    // Defensive: if nothing new was persisted (no unsent lines), still push a delta so UI shows a separate ticket
                    if (!line.length) {
                        try {
                            await this.rpc('/pos/kitchen/push_delta', {
                                shop_id: this.pos.config.id,
                                order_ref: this.pos.get_order().name,
                                ticket_uid: ticketUid,
                                new_lines: newLineSummary,
                                meta: {},
                            });
                        } catch (_) {}
                    }
                    // Eagerly resolve ticket to real line_ids and broadcast to kitchen
                    try {
                        await this.rpc('/pos/kitchen/resolve_ticket', {
                            shop_id: this.pos.config.id,
                            ticket_uid: ticketUid,
                        });
                    } catch (e) { /* ignore */ }
                }
            } finally {
                this.clicked = false;
            }
        }
    },
    hasQuantity(order) {
        if (!order) {
            return false;
        } else {
            return (
                order.orderlines.reduce((totalQty, line) => totalQty + line.get_quantity(), 0) > 0
            );
        }
    },
    get highlightPay() {
        return (
            super.highlightPay &&
            !this.currentOrder.hasChangesToPrint() &&
            this.hasQuantity(this.currentOrder)
        );
    },
    get categoryCount() {
        const orderChange = this.currentOrder.getOrderChanges().orderlines;
        const categories = Object.values(orderChange).reduce((acc, curr) => {
            const categoryId = this.pos.db.product_by_id[curr.product_id].pos_categ_ids[0];
            const category = this.pos.db.category_by_id[categoryId];
            if (category) {
                if (!acc[category.id]) {
                    acc[category.id] = { count: curr.quantity, name: category.name };
                } else {
                    acc[category.id].count += curr.quantity;
                }
            }
            return acc;
        }, {});
        return Object.values(categories);
    },
    get displayCategoryCount() {
        return this.categoryCount.slice(0, 3);
    },
    get isCategoryCountOverflow() {
        if (this.categoryCount.length > 3) {
            return true;
        }
        return false;
    },
});



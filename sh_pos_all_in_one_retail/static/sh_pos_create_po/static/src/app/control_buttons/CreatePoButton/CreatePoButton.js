  /** @odoo-module **/

    import { _t } from "@web/core/l10n/translation";
    import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
    import { useService } from "@web/core/utils/hooks";
    import { Component } from "@odoo/owl";
    import { usePos } from "@point_of_sale/app/store/pos_hook";
    import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
    import { ShPOConfirmPopup } from "@sh_pos_all_in_one_retail/static/sh_pos_create_po/app/Popups/sh_po_confirm_popup/sh_po_confirm_popup";

    export class CreatePoButton extends Component {
        static template = "sh_pos_create_po.CreatePoButton";
        setup() {
            this.pos = usePos();
            this.popup = useService("popup");
        }
        async onClick() {
            var self = this;
            var order = this.pos.get_order()
            var orderlines = order.get_orderlines()
            var client = order.get_partner();
            if (client != null) {
                var purchase_payment_term = false
                if (client && client.property_supplier_payment_term_id) {
                    purchase_payment_term = client.property_supplier_payment_term_id[0]
                }
                if (orderlines.length != 0) {
                    try {
                        var orderLines = []
                        order.orderlines.forEach(item => {
                            return orderLines.push(item.export_as_JSON());
                        });
                        var CreatePo = {
                            'partner_id': order.get_partner().id,
                            'payment_term_id': purchase_payment_term,
                            'order_lines': orderLines,
                        }
                        
                        self.pos.db.all_purchase_orders.push(CreatePo)

                        var Orders = await self.pos.create_purchase_order()
                        if (Orders && Orders.length > 0) {
                            self.popup.add(ShPOConfirmPopup, {
                                title: 'Purchase Order Reference',
                                body: " Purchase Order Created.",
                                PurhcaseOrderId: Orders[0].id,
                                PurchaseOrderName: Orders[0].name
                            })
                        }
                    } catch (error) {
                        this.pos.set_synch('disconnected');
                    }
                }
                else {
                    this.popup.add(ErrorPopup, {
                        title: 'Product is not available !',
                        body: 'Please Add Product In Cart !',
                    });
                }
            }
            else {
                this.popup.add(ErrorPopup, {
                    title: 'Partner is not available !',
                    body: 'Please Select Partner!',
                });
            }
        }
    }

    ProductScreen.addControlButton({
        component: CreatePoButton,
        condition: function () {
            return this.pos.config.sh_dispaly_purchase_btn
        },
    })

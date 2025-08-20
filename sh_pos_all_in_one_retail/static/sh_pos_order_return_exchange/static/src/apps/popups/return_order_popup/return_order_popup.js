/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
import { onMounted, useRef, useState } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";


export class ReturnOrderPopup extends AbstractAwaitablePopup {
    static template = "ReturnOrderPopup";

    setup() {
        super.setup();
        this.pos = usePos()
        this.returnLines = []
        this.order = this.props.order
        onMounted(this.onMounted);
    }
    sh_input_qty(ev){
        var val = ev.target.value
        var max_val = $(ev.target).attr('max-qty')
        if ( !this.pos.config.sh_return_more_qty ){
            if( parseFloat(val) > parseFloat(max_val)) {
                $(ev.target).addClass('more_qty')
                ev.target.value = ""            
            }else{
                $(ev.target).removeClass('more_qty')
            }
        }else{
            if( this.props.exchange_order && parseFloat(val) > parseFloat(max_val)) {
                $(ev.target).addClass('more_qty')
                ev.target.value = ""            
            }else{
                $(ev.target).removeClass('more_qty')
            }
        }
    }
    set_return_lines() {
        var self = this; 
        for (let input of $('.sh-qty')) {
            var val = $(input).val()
            if (val) {
                let line_id = $(input).attr('line-id')
                var dict = { line_id: line_id, qty: parseFloat(val)}
                self.returnLines.push(dict)
            }
        }
    }

    async sh_exchange(ev){
        var self = this;
        this.set_return_lines()
        var order = this.pos.get_order()
        if ( this.returnLines ) {
            [...order.get_orderlines()].map(async (line) => await order.removeOrderline(line))
            var exchange_same_product = $('#exchange_checkbox').is(':checked')
            for ( let return_line of this.returnLines ) {
                let line_data = self.pos.db.pos_order_line_by_id[return_line.line_id]
                if (line_data) {
                    let return_qty = return_line.qty
                    let product = self.pos.db.get_product_by_id(line_data.product_id)
                    if (product && (!product.sh_product_non_exchangeable) ){
                        await order.add_product(product, {
                            quantity: -(return_qty),
                            price_unit: line_data.price_unit,
                            'sh_line_id': line_data.id,
                            merge: false,
                        })
                        if (exchange_same_product){
                            await order.add_product(product, {
                                quantity: return_qty,
                                price_unit: line_data.price_unit,
                                merge: false,
                            })
                        }
                    }
                    
                }
            }
            order.is_exchange_order = true
            order.old_pos_reference = this.order.pos_reference
            order.old_pos_order_id = this.order.id
            if (this.order && this.order.partner_id){
                var partner = this.pos.db.get_partner_by_id(this.order.partner_id)
                order.set_partner(partner)
            }
            this.confirm()
            self.pos.showScreen('ProductScreen')
        }
    }
    async sh_total_retun(ev){
        var self = this;
        var order = this.pos.get_order()
        if ( this.returnLines ) {
            [...order.get_orderlines()].map(async (line) => await order.removeOrderline(line))

            for ( let return_line of  this.props.lines ) {
                if (return_line) {
                    let qty = return_line.qty
                    if ( (qty - return_line.sh_return_qty) > 0 ){
                        let product = self.pos.db.get_product_by_id(return_line.product_id)
                        if (product && (!product.sh_product_non_returnable || !product.sh_product_non_exchangeable) ){
                            order.add_product(product, {
                                quantity: -(qty - return_line.sh_return_qty),
                                price_unit: return_line.price_unit,
                                'sh_line_id': return_line.id,
                                discount: return_line.discount
                            })
                        }
                    }
                }
            }
            order.is_return_order = true
            order.old_pos_reference = this.order.pos_reference || this.order.name
            order.old_pos_order_id = this.order.id || this.order.server_id

            if (this.order && this.order.partner_id){
                var partner = this.pos.db.get_partner_by_id(this.order.partner_id)
                order.set_partner(partner)
            }

            this.confirm()
            self.pos.showScreen('PaymentScreen')
        }
    }

    async sh_total_exchange(ev){
        var self = this;
        var order = this.pos.get_order()
        if ( this.returnLines ) {
            [...order.get_orderlines()].map(async (line) => await order.removeOrderline(line))

            for ( let return_line of  this.props.lines ) {
                if (return_line) {
                    let qty = return_line.qty
                    var exchange_same_product = $('#exchange_checkbox').is(':checked')
                    if ( (qty - return_line.sh_return_qty) > 0 ){
                        let product = self.pos.db.get_product_by_id(return_line.product_id)
                        if (product && (!product.sh_product_non_exchangeable) ){
                            order.add_product(product, {
                                quantity: -(qty - return_line.sh_return_qty),
                                price_unit: return_line.price_unit,
                                'sh_line_id': return_line.id
                            })
                            if (exchange_same_product){
                                order.add_product(product, {
                                    quantity: qty - return_line.sh_return_qty,
                                    price_unit: return_line.price_unit,
                                    merge: false,
                                })
                            }
                        }
                    }
                }
            }
            order.is_exchange_order = true
            order.old_pos_reference = this.order.pos_reference
            order.old_pos_order_id = this.order.id
            if (this.order && this.order.partner_id){
                var partner = this.pos.db.get_partner_by_id(this.order.partner_id)
                order.set_partner(partner)
            }
            this.confirm()
            self.pos.showScreen('ProductScreen')
        }
    }
    async sh_retun(ev) {
        var self = this;
        this.set_return_lines()
        var order = this.pos.get_order()
        if ( this.returnLines ) {
            [...order.get_orderlines()].map(async (line) => await order.removeOrderline(line))

            for ( let return_line of this.returnLines ) {
                let line_data = self.pos.db.pos_order_line_by_id[return_line.line_id]
                if (line_data) {
                    let return_qty = return_line.qty
                    let product = self.pos.db.get_product_by_id(line_data.product_id)
                    order.add_product(product, {
                        quantity: -(return_qty),
                        price_unit: line_data.price_unit,
                        'sh_line_id': line_data.id,
                        discount:line_data.discount
                    })
                }
            }
            order.is_return_order = true
            order.old_pos_reference = this.order.pos_reference || this.order.name
            order.old_pos_order_id = this.order.id || this.order.server_id
            if (this.order && this.order.partner_id){
                var partner = this.pos.db.get_partner_by_id(this.order.partner_id)
                order.set_partner(partner)
            }
            this.confirm()
            self.pos.showScreen('PaymentScreen')
        }

    }

    onMounted() {
        console.log('POPUP', this);
    }
    getPayload() {
        return ""
    }
}

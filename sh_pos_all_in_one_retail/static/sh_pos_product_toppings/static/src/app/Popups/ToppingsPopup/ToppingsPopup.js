/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
import { usePos } from "@point_of_sale/app/store/pos_hook";
// import { ReceiptScreen } from "@point_of_sale/../tests/tours/helpers/ReceiptScreenTourMethods";
import { useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { formatFloat, formatMonetary } from "@web/views/fields/formatters";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";

export class ToppingsPopup extends AbstractAwaitablePopup {
    static template = "sh_pos_product_toppings.ToppingsPopup";
    setup() {
        super.setup();
        this.pos = usePos();
        this.numberBuffer = useService("number_buffer");
          this.popup = useService("popup");
        // useListener('click-topping-product', this._clicktoppigProduct);
        // Wizard state for grouped flow
        this.state = useState({ currentIndex: 0, selectedByGroup: {} });
        this.baseProduct = this.props.base_product || null;
        // Resolve groups for the base product (if provided)
        const groupIds = (this.baseProduct && this.baseProduct.sh_topping_group_ids) || [];
        const groupsById = (this.pos.db && this.pos.db.topping_groups_by_id) || {};
        this.groups = groupIds.map((gid) => groupsById[gid]).filter((g) => !!g);
    }
    ClickOk(){ 
        if (this.hasGroups && !this.canFinish()) {
            this.popup.add(ErrorPopup, { title: _t('Please complete required selections') });
            return;
        }
        this.props.resolve({ confirmed: true, payload: null });
        this.cancel();
    }
    get globalToppings(){
        return this.props.Globaltoppings
    }
    get toppingProducts(){
        return this.props.Topping_products
    }
    get hasGroups() {
        return this.groups && this.groups.length > 0;
    }
    get currentGroup() {
        if (!this.hasGroups) return null;
        return this.groups[this.state.currentIndex];
    }
    groupMin(group) {
        return (group && typeof group.min === 'number') ? group.min : 0;
    }
    groupMax(group) {
        return (group && typeof group.max === 'number') ? group.max : 0;
    }
    currentSelectedCount() {
        const gid = this.currentGroup?.id;
        if (!gid) return 0;
        return this.state.selectedByGroup[gid] || 0;
    }
    canProceedCurrent() {
        const g = this.currentGroup;
        if (!g) return true;
        const min = this.groupMin(g) || 0;
        return this.currentSelectedCount() >= min;
    }
    canFinish() {
        if (!this.hasGroups) return true;
        for (const g of this.groups) {
            const min = this.groupMin(g) || 0;
            const got = this.state.selectedByGroup[g.id] || 0;
            if (got < min) return false;
        }
        return true;
    }
    get stepLabel() {
        if (!this.hasGroups) return "";
        return `${this.state.currentIndex + 1}/${this.groups.length}`;
    }
    nextGroup() {
        if (!this.hasGroups) return;
        if (!this.canProceedCurrent()) {
            this.popup.add(ErrorPopup, { title: _t('Please select required toppings for this group') });
            return;
        }
        if (this.state.currentIndex < this.groups.length - 1) {
            this.state.currentIndex += 1;
        }
    }
    isCurrentOptional() {
        const g = this.currentGroup;
        return !!g && (this.groupMin(g) || 0) === 0;
    }
    skipCurrent() {
        if (!this.hasGroups) return;
        if (this.state.currentIndex < this.groups.length - 1) {
            this.state.currentIndex += 1;
        } else {
            // Last optional group: finish directly
            this.ClickOk();
        }
    }
    prevGroup() {
        if (!this.hasGroups) return;
        if (this.state.currentIndex > 0) {
            this.state.currentIndex -= 1;
        }
    }
    productsForGroup(group) {
        if (!group) return [];
        // Intersect provided topping products with the group's topping ids
        const allowedIds = new Set(group.toppinds_ids || []);
        return (this.toppingProducts || []).filter((p) => allowedIds.has(p.id));
    }
    groupAllowedIdSet() {
        const g = this.currentGroup;
        return new Set((g && g.toppinds_ids) || []);
    }
    get imageUrl() {
        const product = this.product; 
        return `/web/image?model=product.product&field=image_128&id=${product.id}&write_date=${product.write_date}&unique=1`;
    }
    imageUrlFor(product) {
        return `/web/image?model=product.product&field=image_128&id=${product.id}&write_date=${product.write_date}&unique=1`;
    }
    get pricelist() {
        const current_order = this.pos.get_order();
        if (current_order) {
            return current_order.pricelist;
        }
        return this.pos.default_pricelist;
    }
    get price() {
        const { currencyId, digits } = this.env;
        const formattedUnitPrice = formatMonetary(this.product.get_price(this.pricelist, 1), { currencyId, digits });

        if (this.product.to_weight) {
            return `${formattedUnitPrice}/${
                this.pos.units_by_id[this.product.uom_id[0]].name
            }`;
        } else {
            return formattedUnitPrice;
        }
    }
    priceFor(product) {
        const { currencyId, digits } = this.env;
        const formattedUnitPrice = formatMonetary(product.get_price(this.pricelist, 1), { currencyId, digits });
        if (product.to_weight) {
            return `${formattedUnitPrice}/${this.pos.units_by_id[product.uom_id[0]].name}`;
        }
        return formattedUnitPrice;
    }
    isSelected(product) {
        const order = this.pos.get_order();
        const line = order && order.get_selected_orderline();
        if (!line || !line.get_toppings) return false;
        const topps = line.get_toppings() || [];
        return topps.some((t) => (t.product_id || (t.product && t.product.id)) === product.id);
    }
    isRadioMode() {
        const g = this.currentGroup;
        if (!g) return false;
        const min = this.groupMin(g) || 0;
        const max = this.groupMax(g) || 0;
        return min === 1 && max === 1;
    }
    async _clicktoppigProduct(event){
        if (!this.pos.get_order()) {
            this.pos.add_new_order();
        }
        const product = event;
        // Radio: enforce single selection per group by replacing
        if (this.hasGroups && this.currentGroup && this.isRadioMode()) {
            const allowed = this.groupAllowedIdSet();
            const order = this.pos.get_order();
            const base = order.get_selected_orderline();
            if (base && base.get_toppings_temp && base.get_toppings_temp().length) {
                const toRemove = base.get_toppings_temp().filter((t) => allowed.has(t.product.id));
                for (const t of toRemove) {
                    // remove child line from order and arrays
                    order.remove_orderline(t);
                }
                if (toRemove.length) {
                    base.Toppings_temp = base.get_toppings_temp().filter((t) => !allowed.has(t.product.id));
                    base.Toppings = (base.get_toppings() || []).filter((d) => !allowed.has(d.product_id));
                    const gid = this.currentGroup.id;
                    this.state.selectedByGroup[gid] = 0;
                }
            }
        }
        // Enforce per-group max before adding
        if (this.hasGroups && this.currentGroup) {
            const gid = this.currentGroup.id;
            const curr = this.state.selectedByGroup[gid] || 0;
            const gmax = this.groupMax(this.currentGroup) || 0;
            if (gmax > 0 && curr >= gmax) {
                await this.popup.add(ErrorPopup, { title: _t('Maximum reached for this group') });
                return;
            }
        }
        if (this.pos.config.sh_enable_toppings && this.pos.get_order() && this.pos.get_order().get_selected_orderline()){
            this.pos.get_order().add_topping_product(product);
            if (this.hasGroups && this.currentGroup) {
                const gid = this.currentGroup.id;
                this.state.selectedByGroup[gid] = (this.state.selectedByGroup[gid] || 0) + 1;
            }
        }else{
            await this.popup.add(ErrorPopup, {
                title: 'Please Select Orderline !',
            });
            // await  this.popup.add(ErrorPopup, {title : 'Please Select Orderline !',body: '123'});
                
            // this.showPopup('ErrorPopup', { 
            //     title: 'Please Select Orderline !'
            // })
        }
        this.numberBuffer.reset();
    }
    removeTopping(ev, product) {
        // prevent triggering row click add
        if (ev && ev.stopPropagation) ev.stopPropagation();
        const order = this.pos.get_order();
        const base = order && order.get_selected_orderline();
        if (!base) return;
        const temp = base.get_toppings_temp && base.get_toppings_temp();
        if (!temp || !temp.length) return;
        const toRemove = temp.filter((t) => t.product && t.product.id === product.id);
        for (const t of toRemove) {
            order.remove_orderline(t);
        }
        base.Toppings_temp = temp.filter((t) => !(t.product && t.product.id === product.id));
        base.Toppings = (base.get_toppings() || []).filter((d) => d.product_id !== product.id);
        if (this.hasGroups && this.currentGroup) {
            const gid = this.currentGroup.id;
            const curr = this.state.selectedByGroup[gid] || 0;
            this.state.selectedByGroup[gid] = Math.max(0, curr - toRemove.length);
        }
        if ((base.Toppings || []).length === 0) {
            base.set_is_has_topping(false);
        }
    }
}
  

/** @odoo-module */

import { Order, Orderline} from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";
import {
    formatFloat,
    roundDecimals as round_di,
    roundPrecision as round_pr,
    floatIsZero,
} from "@web/core/utils/numbers";

patch(Orderline.prototype, {
    // When a parent orderline quantity changes, keep toppings in sync
    set_quantity() {
        const prevQty = this.get_quantity();
        const res = super.set_quantity(...arguments);
        try {
            // Only propagate from a parent (non-topping) line that has toppings
            if (!this.is_topping && this.get_is_has_topping && this.get_is_has_topping()) {
                const children = this.get_toppings_temp && this.get_toppings_temp();
                if (children && children.length) {
                    const parentQty = this.get_quantity();
                    const safePrev = prevQty || 0;
                    // Avoid divide by zero; if previous was 0, just use each child's ratio if set
                    for (const child of children) {
                        // Determine desired quantity per parent unit
                        let perParent = child.sh_qty_per_parent;
                        if (perParent === undefined || perParent === null) {
                            if (safePrev > 0) {
                                perParent = child.get_quantity() / safePrev;
                            } else {
                                // Default to 1 child per 1 parent when no history
                                perParent = 1;
                            }
                        }
                        const newChildQty = perParent * parentQty;
                        child.set_quantity(newChildQty);

                        // Keep the parent-side summary dict up to date
                        if (this.Toppings && this.Toppings.length) {
                            const j = this.Toppings.findIndex((d) => d && d.id === child.id);
                            if (j >= 0) {
                                const d = this.Toppings[j];
                                d.quantity = child.get_quantity();
                                d.quantityStr = child.quantityStr;
                                d.price_subtotal = child.get_price_without_tax();
                                d.price_subtotal_incl = child.get_price_with_tax();
                                d.price_display = child.get_display_price();
                            }
                        }
                    }
                }
            } else if (this.is_topping && this.sh_topping_parent) {
                // If a topping itself is edited, refresh its ratio relative to parent
                const parent = this.sh_topping_parent;
                const parentQtyNow = parent && parent.get_quantity ? parent.get_quantity() : 1;
                this.sh_qty_per_parent = this.get_quantity() / (parentQtyNow || 1);
                // and keep the parent's summary dict in sync
                if (parent && parent.Toppings && parent.Toppings.length) {
                    const j = parent.Toppings.findIndex((d) => d && d.id === this.id);
                    if (j >= 0) {
                        const d = parent.Toppings[j];
                        d.quantity = this.get_quantity();
                        d.quantityStr = this.quantityStr;
                        d.price_subtotal = this.get_price_without_tax();
                        d.price_subtotal_incl = this.get_price_with_tax();
                        d.price_display = this.get_display_price();
                    }
                }
            }
        } catch (err) {
            console && console.warn && console.warn('Topping qty sync failed:', err);
        }
        return res;
    },
    setup(_defaultObj, options) {
        super.setup(...arguments);
        if(options.json){
            this.is_topping = options.json.sh_is_topping[0]
            this.is_has_topping = options.json.sh_is_has_topping[0];
        }
    },
    init_from_JSON(json) {
        var self = this
        super.init_from_JSON(...arguments);
        this.is_has_topping = json.is_has_topping;
        this.is_topping = json.is_topping || false;
        this.topping = json.topping || null
        this.Toppings_temp = json.Toppings_temp || []
        this.Toppings = json.Toppings || []
        this.Toppings.forEach(function (each, key) {
            var orderline = new Orderline({}, {
                pos: self.pos,
                order: self.order,
                id: each.id,
                product: self.pos.db.get_product_by_id(each.product_id),
                price: each.price,
            });
            orderline.set_quantity(each.quantity)
            self.Toppings_temp[key] = orderline
        });
    },
    export_as_JSON() {
        var res = super.export_as_JSON(...arguments);
        res['is_has_topping'] = this.is_has_topping;
        res['sh_is_has_topping'] = this.is_has_topping;
        res['is_topping'] = this.is_topping || false;
        res['sh_is_topping'] = this.is_topping || false;
        return res
    },
    get_is_has_topping() {
        return this.is_has_topping
    },
    set_is_has_topping(is_has_topping) {
        this.is_has_topping = is_has_topping
    },
    export_for_printing() {
        let result = super.export_for_printing(...arguments);
        result['is_has_topping'] = this.is_has_topping || false;
        result['Toppings'] = this.Toppings || []
        result['is_topping'] = this.is_topping || false

        return result;
    },
    get_topping() {
        return this.topping || []
    },
    set_topping(topping) {
        this.topping = topping
    },
    get_toppings() {
        return this.Toppings || []
    },
    set_toppings(Toppings) {
        if (!this.Toppings) {
            this.Toppings = [Toppings]
        } else {
            this.Toppings.push(Toppings)
        }
    },
    get_toppings_temp() {
        return this.Toppings_temp || []
    },
    set_toppings_temp(Toppings) {
        if (!this.Toppings_temp) {
            this.Toppings_temp = [Toppings]
        } else {
            this.Toppings_temp.push(Toppings)
        }
    },
    can_be_merged_with(orderline) {
        if (this.pos.config.sh_enable_toppings && this.pos.config.sh_allow_same_product_different_qty) {
            if (this.is_has_topping) {
                return false
            } else if (!this.is_topping) {
                if (orderline.product.sh_topping_ids.length){
                    return false
                }else{
                    return super.can_be_merged_with(orderline);
                }
            } else {
                // super.can_be_merged_with.apply(this, arguments);
                return false
            }
        } else if (!this.is_topping) {
            return super.can_be_merged_with(orderline);
        } else {
            return false
        }
    },
    /**
     * override
     */
    getDisplayClasses() {
        return {
            ...super.getDisplayClasses(),
            "sh-is-topping": this.is_topping ? this.is_topping : false,
        };
    },
    toppings_can_be_merged_with(orderline) {
        var price = parseFloat(round_di(this.price || 0, this.pos.dp['Product Price']).toFixed(this.pos.dp['Product Price']));
        var order_line_price = orderline.product.get_price(this.order.pricelist, this.get_quantity());
        order_line_price = this.compute_fixed_price(order_line_price);
        if (this.get_product().id !== orderline.get_product().id) {    //only orderline of the same product can be merged
            return false;
        } else if (!this.get_unit() || !this.get_unit().is_pos_groupable) {
            return false;
        } else if (this.get_discount() > 0) {             // we don't merge discounted orderlines
            return false;
        } else if (this.product.tracking == 'lot' && (this.pos.picking_type.use_create_lots || this.pos.picking_type.use_existing_lots)) {
            return false;
        } else if (this.description !== orderline.description) {
            return false;
        } else if (this.get_customer_note() !== this.get_customer_note()) {
            return false;
        } else if (this.refunded_orderline_id) {
            return false;
        } else {
            return true;
        }
    },

    getDisplayData() {
        let res = super.getDisplayData();
        res['is_has_topping'] = this.is_has_topping;
        res['Toppings'] = this.Toppings;
        res['is_topping'] = this.is_topping;
        
        return res
    }
});
patch(Order.prototype, {
    setup(obj, options) {
        super.setup(...arguments)
        if (this.get_orderlines() && this.get_orderlines().length) {
            let parentline = false
            if (this.get_orderlines() && this.get_orderlines().length) {
                let parentline = false
                for (let line of this.get_orderlines()) {
                    if (line.is_has_topping) {
                        parentline = line
                    } else {
                        var dic = {
                            quantity: line.get_quantity(),
                            quantityStr: line.quantityStr,
                            price_unit: line.get_unit_price(),
                            price_subtotal: line.get_price_without_tax(),
                            price_subtotal_incl: line.get_price_with_tax(),
                            discount: line.get_discount(),
                            product_id: line.product.id,
                            product: line.get_product(),
                            unit: line.product.get_unit().name,
                            tax_ids: [[6, false, line.get_applicable_taxes().map((tax) => tax.id)]],
                            id: line.id,
                            description: line.description,
                            full_product_name: line.get_full_product_name(),
                            price_extra: line.get_price_extra(),
                            price_display: line.get_display_price(),
                            customer_note: line.get_customer_note(),
                            refunded_orderline_id: line.refunded_orderline_id,
                            price_manually_set: line.price_manually_set,
                            parent_orderline_id: parentline.id,
                            parent_orderline: parentline,
                        }
                        if (parentline) {
                            if (line.is_topping) {
                                parentline.set_toppings_temp(line)
                                parentline.set_toppings(dic)
                            }
                        }
                    }
                }
            }
        }
    },
    removeOrderline(line) {
        var self = this;
        if (line.Toppings) {
            line.Toppings.forEach(function (each_topping) {
                if (each_topping && each_topping.id) {
                    self.removeOrderline(self.get_orderline(each_topping.id));
                }
            })
        }
        var res = super.removeOrderline(line)
        return res
    },
    export_as_JSON() {
        var self = this;
        const json = super.export_as_JSON(...arguments);

        var orderLines = []

        for (var i = 0; i < self.get_orderlines().length; i++) {
            var item = self.get_orderlines()[i]
            if (item) {
                if (item.Toppings) {
                    item['Toppings'] = item.Toppings
                }
                if (item.is_topping) {
                    item['is_topping'] = item.is_topping
                }
                orderLines.push([0, 0, item.export_as_JSON()]);
            }
        }
        if (orderLines && orderLines.length > 0) {
            json['lines'] = orderLines;
        }
        return json
    },
    get_last_orderline() {
        const regularLines = this.get_orderlines
            .apply(this, arguments)
            .filter((line) => !line.is_topping);
        return regularLines[regularLines.length - 1];
    },

    async add_topping_product(product, options) {
        this.assert_editable();
        var self = this;
        options = options || {};
        var SelectedOrderline = this.get_selected_orderline()
        SelectedOrderline.set_is_has_topping(true)
        var line = new Orderline(
            { env: this.env },
            {
                pos: this.pos,
                order: this,
                product: product,
            }
        );
        line.is_topping = true
        this.fix_tax_included_price(line);
        this.set_orderline_options(line, options);
        line.set_full_product_name();
        // remember the child-per-parent ratio so we can scale on parent qty changes
        try {
            const parentQty = SelectedOrderline.get_quantity() || 1;
            line.sh_qty_per_parent = line.get_quantity() / (parentQty || 1);
        } catch (e) { /* no-op */ }
        var product_ids = []
        var to_merge_orderline;
        if (SelectedOrderline.get_toppings_temp() && SelectedOrderline.get_toppings_temp().length) {
            for (var i = 0; i < SelectedOrderline.get_toppings_temp().length; i++) {
                if (SelectedOrderline.get_toppings_temp().at(i).toppings_can_be_merged_with(line) && options.merge !== false) {
                    to_merge_orderline = SelectedOrderline.get_toppings_temp().at(i)
                }
            }
        }
        if (to_merge_orderline) {
            to_merge_orderline.merge(line);
            to_merge_orderline.sh_topping_parent = SelectedOrderline;
            try {
                const parentQty = SelectedOrderline.get_quantity() || 1;
                to_merge_orderline.sh_qty_per_parent = to_merge_orderline.get_quantity() / (parentQty || 1);
            } catch (e) { /* no-op */ }
            var dic1 = {
                quantity: to_merge_orderline.get_quantity(),
                quantityStr: to_merge_orderline.quantityStr,
                price_unit: to_merge_orderline.get_unit_price(),
                price_subtotal: to_merge_orderline.get_price_without_tax(),
                price_subtotal_incl: to_merge_orderline.get_price_with_tax(),
                discount: to_merge_orderline.get_discount(),
                product_id: product.id,
                product: product,
                unit: to_merge_orderline.product.get_unit().name,
                tax_ids: [[6, false, this.get_selected_orderline().get_applicable_taxes().map((tax) => tax.id)]],
                id: to_merge_orderline.id,
                price_display: to_merge_orderline.get_display_price(),
                description: to_merge_orderline.description,
                full_product_name: to_merge_orderline.get_full_product_name(),
                price_extra: to_merge_orderline.get_price_extra(),
                customer_note: to_merge_orderline.get_customer_note(),
                refunded_orderline_id: to_merge_orderline.refunded_orderline_id,
                price_manually_set: to_merge_orderline.price_manually_set,
                parent_orderline_id: SelectedOrderline.id,
                parent_orderline: SelectedOrderline,
            }
            SelectedOrderline.get_toppings_temp().forEach(function (eachtopping, key) {
                if (eachtopping.product.id == dic1.product.id) {
                    SelectedOrderline.Toppings[key] = dic1
                }
            });

            SelectedOrderline.set_topping(to_merge_orderline)
            if (self.get_orderline(to_merge_orderline.id)) {
                self.get_orderline(to_merge_orderline.id).set_quantity(to_merge_orderline.quantity)
            }

        } else {
            var dic = {
                quantity: line.get_quantity(),
                quantityStr: line.quantityStr,
                price_unit: line.get_unit_price(),
                price_subtotal: line.get_price_without_tax(),
                price_subtotal_incl: line.get_price_with_tax(),
                discount: line.get_discount(),
                product_id: product.id,
                product: product,
                unit: line.product.get_unit().name,
                tax_ids: [[6, false, this.get_selected_orderline().get_applicable_taxes().map((tax) => tax.id)]],
                id: line.id,
                description: line.description,
                full_product_name: line.get_full_product_name(),
                price_extra: line.get_price_extra(),
                price_display: line.get_display_price(),
                customer_note: line.get_customer_note(),
                refunded_orderline_id: line.refunded_orderline_id,
                price_manually_set: line.price_manually_set,
                parent_orderline_id: SelectedOrderline.id,
                parent_orderline: SelectedOrderline,
            }
            SelectedOrderline.set_topping(line);
            SelectedOrderline.set_toppings_temp(line)
            SelectedOrderline.set_toppings(dic);
            line['sh_topping_parent'] = SelectedOrderline
            self.pos.get_order().add_orderline(line)
        }
        self.pos.get_order().select_orderline(SelectedOrderline);


        // if (options.draftPackLotLines) {
        //     SelectedOrderline.setPackLotLines(options.draftPackLotLines);
        // }
    }
});

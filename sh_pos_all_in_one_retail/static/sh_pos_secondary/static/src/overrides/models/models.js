/** @odoo-module */

import { Order, Orderline , Product } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";

// patch(Product.prototype, {
   
//     getFormattedUnitPrice(){
//         let res = super.getFormattedUnitPrice()
//         if(this.sh_secondary_uom && this.sh_is_secondary_unit && this.pos.config.enable_price_to_display && this.pos.config.select_uom_type == 'secondary' ){
//             let unit_price=   this.get_display_price()
//             var secondary = this.get_product_secondary_unit(this.sh_secondary_uom)
//             var primary = this.pos.units_by_id[1]
//             var k = this.convert_product_qty_uom(1, primary, secondary)
//             return this.env.utils.formatCurrency(unit_price * k)
//         }else{
//             return res
//         }
//     },
//     convert_product_qty_uom(quantity, to_uom, from_uom) {
//         var to_uom = to_uom;
//         var from_uom = from_uom;
//         var from_uom_factor = from_uom.factor;
//         var amount = quantity / from_uom_factor;
//         if (to_uom) {
//             var to_uom_factor = to_uom.factor;
//             amount = amount * to_uom_factor;
//         }
//         return amount;
//     },
//     get_product_secondary_unit(secondary_unit_id){
//         if (!secondary_unit_id) {
//             return this.props.product.get_unit()
//         }
//         secondary_unit_id = secondary_unit_id[0];
//         if (!this.pos) {
//             return undefined;
//         }

//         return this.pos.units_by_id[secondary_unit_id];
//     }
// })

// patch(Order.prototype, {
//     set_pricelist(pricelist) {
//         var self = this;
//         this.pricelist = pricelist;

//         var lines_to_recompute = this.get_orderlines().filter((line) => {
//             return !line.price_manually_set;
//         });
//         lines_to_recompute.forEach((line) => {
//             var primary_uom = line.get_unit();
//             var secondary_uom = line.get_secondary_unit();
//             var current_uom = line.get_current_uom() || primary_uom;
//             if (current_uom == primary_uom) {
//                 line.set_unit_price(line.product.get_price(self.pricelist, line.get_quantity()));
//                 self.fix_tax_included_price(line);
//             } else {
//                 line.set_unit_price(line.product.get_price(self.pricelist, line.get_primary_quantity()));
//                 self.fix_tax_included_price(line);
//             }
//         });
//     }
// });

patch(Order.prototype, {
    async add_product(product, options) {
        let res = await super.add_product(...arguments)
        if(res && options && options.sh_uom_id){
            let uom = this.pos.units_by_id[options.sh_uom_id]
            console.log("=============>", res);
            
            res.set_custom_uom(uom)
        }
        return res 
    }

});
patch(Orderline.prototype, {
    // setup() {
    //     super.setup(...arguments);
    //     console.log("this.sh_uom_id ", this.sh_uom_id, this);
    //     this.sh_uom_id = this.sh_uom_id || false
        
    // },
    init_from_JSON (json) {
        super.init_from_JSON(...arguments);
        if(json.sh_uom_id){
            console.log("json.sh_uom_id", json.sh_uom_id);
            
        }
        this.sh_uom_id = json.sh_uom_id || false
        
    },
    export_as_JSON() {
        var vals = super.export_as_JSON(...arguments);
        if (this.get_custom_uom() && this.get_custom_uom() != this.get_unit()) {
            vals.sh_uom_id = this.get_custom_uom().id;
        }
        console.log("vals", vals);
        
        return vals;
    },
    getDisplayData() {
        let result = super.getDisplayData()
        console.log("this.get_custom_uom() 11111",this, this.get_custom_uom());
        if(this.get_custom_uom()){
            console.log("this.get_custom_uom()",this, this.get_custom_uom());
            result["unit"] = this.get_custom_uom().name ? this.get_custom_uom().name : this.pos.units_by_id[this.get_custom_uom()]?.name
        }
        console.log("result ==>", result);
        
        return result
    },
    set_custom_uom(uom_name){
        console.log("uom_name", uom_name);
        if(uom_name.uom_id){
            let uom = this.pos.units_by_id[uom_name.uom_id]
            this.sh_uom_id = uom
        }else{
            this.sh_uom_id = uom_name
        }
    },
    get_custom_uom(){
        return this.sh_uom_id
    }

});

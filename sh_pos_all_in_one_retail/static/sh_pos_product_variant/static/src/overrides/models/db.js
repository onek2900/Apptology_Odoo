/** @odoo-module */
import { PosDB } from "@point_of_sale/app/store/db";
import { patch } from "@web/core/utils/patch";
import { unaccent } from "@web/core/utils/strings";

patch(PosDB.prototype, {
    variant_product_search_string (product) {
        var str = product.display_name;
        if (product.id) {
            str += '|' + product.id;
        }
        if (product.default_code) {
            str += '|' + product.default_code;
        }
        if (product.description) {
            str += '|' + product.description;
        }
        if (product.description_sale) {
            str += '|' + product.description_sale;
        }
        str = product.id + ':' + str.replace(/:/g, '') + '\n';
        return str;
    },
    // add_products(products){
    //     super.add_products(products);
    //     var self = this;
    //     for(let product of products){
    //         if (product){
    //             if (self.product_by_tmpl_id && self.product_by_tmpl_id[product.product_tmpl_id[0]]){
    //                 self.product_by_tmpl_id[product.product_tmpl_id[0]].push(product.id)
    //             }else{
    //                 self.product_by_tmpl_id[product.product_tmpl_id[0]] = [product.id]
    //                 if(product.sh_alternative_products){
    //                     self.alternative_product_by_id[product.product_tmpl_id] = product.sh_alternative_products
    //                 }
    //             }
    //         }
    //     }
    // },
    search_variants(variants, query) {
        var self = this;
        this.variant_search_string = ""
        for (var i = 0; i < variants.length; i++) {
            var variant = variants[i]
            var search_variant = unaccent(self.variant_product_search_string(variant))
            self.variant_search_string += search_variant
        }
        try {
            query = query.replace(/[\[\]\(\)\+\*\?\.\-\!\&\^\$\|\~\_\{\}\:\,\\\/]/g, '.');
            query = query.replace(/ /g, '.+');
            var re = RegExp("([0-9]+):.*?" + unaccent(query), "gi");
        } catch (e) {
            return [];
        }

        var results = [];
        for (var i = 0; i < this.limit; i++) {
            var pariant_pro = re.exec(this.variant_search_string)
            if (pariant_pro) {
                var id = Number(pariant_pro[1]);
                var product_var = this.get_product_by_id(id)

                results.push(product_var)

            } else {
                break;
            }
        }
        return results;
    },
})

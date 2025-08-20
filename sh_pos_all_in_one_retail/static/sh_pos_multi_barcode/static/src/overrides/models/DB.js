/** @odoo-module */
import { PosDB } from "@point_of_sale/app/store/db";
import { patch } from "@web/core/utils/patch";
import { unaccent } from "@web/core/utils/strings";

patch(PosDB.prototype, {
    _product_search_string(product){
        var string = super._product_search_string(product)
        var old_sting = string.split(':')[1]
        var new_sting = old_sting
        for(let each_barcode of Object.values(this.multi_barcode_by_id)){
            if(each_barcode.product_id == product.id){
                if(product["multi_barcodes"]){
                    product["multi_barcodes"] += '|' + each_barcode.name
                }
                else{
                    product["multi_barcodes"] = each_barcode.name
                }
            }
        }
        if (product.multi_barcodes){
            new_sting = product.multi_barcodes + '|' + new_sting
        }
       
        var str_list = [string.split(':')[0], new_sting]
        string = str_list.join(":") 
        return string
    }
})

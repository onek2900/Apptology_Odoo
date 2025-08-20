/** @odoo-module */

import { ProductsWidget } from "@point_of_sale/app/screens/product_screen/product_list/product_list";
import { patch } from "@web/core/utils/patch";
import { Component } from "@odoo/owl";
import { ProductCard } from "@point_of_sale/app/generic_components/product_card/product_card";
class SuggestedProductList extends Component {
  static components = { ProductCard };
}
SuggestedProductList.template = "pos_product_suggestion.SuggestedProductList";

patch(ProductsWidget.prototype, {
  setup() {
    super.setup();
    this.final_suggest_products = [];
  },
  get_final_suggested_product_ids(products) {
    const self = this;
    const temp_suggest_ids = new Set(); // Use a Set to store unique IDs
    const final_suggest_products = [];

    for (const product of products) {
      if (product.suggestion_line && product.suggestion_line.length > 0) {
        for (const sug_line of product.suggestion_line) {
          temp_suggest_ids.add(sug_line); // Add to the Set
        }
      }
    }

    if (temp_suggest_ids.size > 0) {
      for (const id of temp_suggest_ids) {
        const pro = self.pos.db.get_product_by_id(
          self.pos.suggestion[id].product_suggestion_id
        );
        if (pro) {
          final_suggest_products.push(pro);
        }
      }
    }

    return final_suggest_products;
  },
  get suggestedproduct() {
    if (this.final_suggest_prodcuts && this.final_suggest_prodcuts.length > 0) {
      return this.final_suggest_prodcuts;
    } else {
      return [];
    }
  },
});
ProductsWidget.components["SuggestedProductList"] = SuggestedProductList;

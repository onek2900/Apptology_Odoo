  /** @odoo-module **/

  import { _t } from "@web/core/l10n/translation";
  import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
  import { useService } from "@web/core/utils/hooks";
  import { Component } from "@odoo/owl";
  import { usePos } from "@point_of_sale/app/store/pos_hook";
  import { ToppingsPopup } from "@sh_pos_all_in_one_retail/static/sh_pos_product_toppings/app/Popups/ToppingsPopup/ToppingsPopup";
  import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";

  export class ToppingButton extends Component {
      static template = "sh_pos_product_toppings.ToppingButton";
      setup() {
          this.pos = usePos();
          this.popup = useService("popup");
        }
        async onClick(){
            var self = this;
            var allproducts = []
           
            allproducts = self.pos.db.get_product_by_category(0) ;
            
            var Globaltoppings = $.grep(allproducts, function (product) {
                return product.sh_is_global_topping;
            });
            if (Globaltoppings.length > 0 ){
                let { confirmed } = await  this.popup.add(ToppingsPopup, {'title' : 'Global Topping','Topping_products': [], 'Globaltoppings': Globaltoppings});
                if (confirmed) {
                } else {
                    return;
                }
                // self.showPopup('ToppingsPopup', {'title' : 'Global Topping','Topping_products': [], 'Globaltoppings': Globaltoppings})
            } else{
                let { confirmed } = await  this.popup.add(ErrorPopup, {title : 'No Toppings',body: 'Not Found any Global Topping'});
                if (confirmed) {
                } else {
                    return;
                }
                // self.showPopup('ErrorPopup', { 
                //     title: 'No Toppings',
                //     body: 'Not Found any Global Topping'
                // })
            }
        }
   
  }

  ProductScreen.addControlButton({
      component: ToppingButton,
      condition: function () {
          return this.pos.config.sh_enable_toppings
      },
  })

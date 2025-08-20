  /** @odoo-module **/

    import { _t } from "@web/core/l10n/translation";
    import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
    import { useService } from "@web/core/utils/hooks";
    import { Component } from "@odoo/owl";
    import { usePos } from "@point_of_sale/app/store/pos_hook";
    import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
    import { ConfirmPopup } from "@point_of_sale/app/utils/confirm_popup/confirm_popup";

    export class RemoveAllItemButton extends Component {
        static template = "sh_pos_all_in_one_retail.RemoveAllItemButton";
        setup() {
            this.pos = usePos();
            this.popup = useService("popup");
        }
        async onClick() {
            var self = this;
            if (this.pos.get_order() && this.pos.get_order().get_orderlines() && this.pos.get_order().get_orderlines().length > 0) {
                var orderlines = this.pos.get_order().get_orderlines();
                if(self.pos.config.sh_remove_all_item && self.pos.config.sh_validation_to_remove_all_item){
                    const { confirmed } = await self.popup.add(ConfirmPopup, {
                        title: "Delete Items",
                        body:(
                            'Do you want remove all items?'
                        ),
                    });
                    if (confirmed) {
                        [...orderlines].map(async(line)=>await self.pos.get_order().removeOrderline(line))
                    }
                }
                else{
                    [...orderlines].map(async(line)=>await self.pos.get_order().removeOrderline(line))
                }
            } else {
                this.popup.add(ErrorPopup, { 
                    title: 'Products !',
                    body: 'Cart is Empty !'
                })
            }
        }
    }

    ProductScreen.addControlButton({
        component: RemoveAllItemButton,
        condition: function () {
            return this.pos.config.sh_remove_all_item
        },
    })

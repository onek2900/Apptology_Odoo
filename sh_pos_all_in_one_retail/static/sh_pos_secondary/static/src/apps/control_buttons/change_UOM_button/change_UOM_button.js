  /** @odoo-module **/

    import { _t } from "@web/core/l10n/translation";
    import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
    import { useService } from "@web/core/utils/hooks";
    import { Component } from "@odoo/owl";
    import { usePos } from "@point_of_sale/app/store/pos_hook";
    import { SelectionPopup } from "@point_of_sale/app/utils/input_popups/selection_popup";
    const { DateTime } = luxon;
    import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";

    export class ChangeUOMButton extends Component {
        static template = "sh_pos_secondary.ChangeUOMButton";
        setup() {
            this.pos = usePos();
            this.popup = useService("popup");
        }
        async onClickUOM() {
            var self = this;
            var selectionList = [];
            var line = this.pos.get_order().get_selected_orderline();
            if (line) {
                let product_id = line.product
                let uom_list = []
                if(product_id && product_id.sh_uom_line_ids && product_id.sh_uom_line_ids.length){
                    for (let i = 0; i < product_id.sh_uom_line_ids.length; i++) {
                        const line_id = product_id.sh_uom_line_ids[i];
                        let uom = self.pos.sh_uom_line_by_id[line_id]
                        uom_list.push(uom)
                    }
                    if(uom_list){
                        uom_list = uom_list.map((uom) => {
                            return {
                                id: uom.id,
                                item: uom,
                                label: uom.uom_name,
                                isSelected: false,
                            };
                        })
                    }
                    const { confirmed, payload: selectedUOM } = await self.popup.add(
                        SelectionPopup, {
                            title: _t("Select the UOM"),
                            list: uom_list,
                    });
                    if (selectedUOM) {
                        
                        const priceList = self.pos.getDefaultPricelist();
                        if(priceList){
                            const date = DateTime.now();
                            
                            let pricelistRule =  !priceList
                            ? []
                            : (product_id.applicablePricelistItems[priceList.id] || []).filter((item) =>
                                product_id.isPricelistItemUsable(item, date)
                        );
                        const rule = pricelistRule.find((rule) => !rule.min_quantity || line.get_quantity() >= rule.min_quantity);
                        
                        if(rule && rule.sh_uom_id && rule.sh_uom_id[0] == selectedUOM.uom_id){
                            let uom = self.pos.units_by_id[rule.sh_uom_id[0]]
                            line.set_custom_uom(uom)
                            line.set_unit_price(rule.fixed_price)
                        }else{
                            if(selectedUOM.sh_qty > 0 ){
                                line.set_quantity(selectedUOM.sh_qty)
                            }
                            line.set_custom_uom(selectedUOM)
                            line.set_unit_price(selectedUOM.price)

                        }
                        
                        
                    }else{
                            if(selectedUOM.sh_qty > 0 ){
                                line.set_quantity(selectedUOM.sh_qty)
                            }
                            line.set_custom_uom(selectedUOM)
                            line.set_unit_price(selectedUOM.price)
                        }
                    }   
                }   
            }else{
                this.popup.add(ErrorPopup, {
                    title: _t("Orderline Not Found!"),
                    body: _t("Please Select Orderline."),
                });
            }
        }
    }

    ProductScreen.addControlButton({
        component: ChangeUOMButton,
        condition: function () {
            return true
        },
    })

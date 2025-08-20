/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { useService } from "@web/core/utils/hooks";

export class PriceListPopupWidget extends AbstractAwaitablePopup {
    static template = "point_of_sale.PriceListPopupWidget";

    setup() {
        super.setup()
        this.min_price_pricelist = this.props.min_price_pricelist
        this.pos = usePos();
        this.popup = useService("popup");
    }   
    async onClickPricelistRow(event) {
        var self = this;
        var line = self.pos.get_order().get_selected_orderline();
        $(".pricelist_row.highlight").removeClass("highlight");
        if ($(this).hasClass("highlight")) {
            $(this).removeClass("highlight");
        } else {
            $(".highlight").removeClass("highlight");
            if (!$(this).hasClass("only_read")) {
                $(this).addClass("highlight");
                var price = $($(event.currentTarget).closest("tr").find(".price_td")[0]).attr('data-price')
                if (self.pos.config.sh_min_pricelist_value) {
                    
                    if (self.min_price_pricelist.product_tml_id && self.min_price_pricelist.product_tml_id == "All Products" && price < self.min_price_pricelist.display_price && line.is_added) {
                        this.popup.add(ErrorPopup,{
                            title: 'Price Warning ',
                            body: 'PRICE IS BELOW MINIMUM',
                        })
                    } else if (self.min_price_pricelist.product_tml_id && self.min_price_pricelist.product_tml_id == line.product.product_tmpl_id && price < self.min_price_pricelist.display_price && line.is_added) {
                        this.popup.add(ErrorPopup, {
                            title: 'Price Warning ',
                            body: 'PRICE IS BELOW MINIMUM',
                        })
                    } else {
                        var pricelist_data = self.pos.db.pricelist_by_id[$(event.currentTarget).data("id")];
                        pricelist_data["items"] = [];
                        for(let each_item of pricelist_data.item_ids){
                            var item_data = self.pos.db.pricelist_item_by_id[each_item];
                            pricelist_data["items"].push(item_data);
                        };
                        line.set_pricelist(pricelist_data);
                        console.log('Set unit price');
                        line.set_unit_price(price);
                        self.confirm()
                    }
                } else {
                    var pricelist_data = self.pos.db.pricelist_by_id[$(event.currentTarget).data("id")];
                    pricelist_data["items"] = [];
                    for(let each_item of pricelist_data.item_ids){
                        var item_data = self.pos.db.pricelist_item_by_id[each_item];
                        pricelist_data["items"].push(item_data);
                    };
                    line.set_pricelist(pricelist_data);
                    console.log('set unit price');
                    line.set_unit_price(price);
                    self.confirm()
                }
            }
        }
    }
}

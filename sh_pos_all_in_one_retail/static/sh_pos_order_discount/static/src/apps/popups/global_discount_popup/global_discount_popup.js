/** @odoo-module */

import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { _t } from "@web/core/l10n/translation";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { formatFloat } from "@web/core/utils/numbers";

export class GlobalDiscountPopupWidget extends AbstractAwaitablePopup {
  static template = "sh_pos_all_in_one_retail.GlobalDiscountPopupWidget";
  setup() {
    super.setup();
    this.pos = usePos();
    $(".sh_discount_value").focus();
  }
  async confirm() {
    var self = this;
    this.props.resolve({ confirmed: true, payload: await this.getPayload() });

    if (!$(".sh_discount_value").val()) {
      alert("Enter amount of discount.");
      $(".sh_discount_value").addClass("invalid_number");
    } else if (
      ($(".sh_discount_value").val() &&
        parseFloat($(".sh_discount_value").val()) > 100 &&
        document.getElementById("discount_percentage_radio") &&
        document.getElementById("discount_percentage_radio").checked) ||
      ($(".sh_discount_value").val() &&
        parseFloat($(".sh_discount_value").val()) < 0) ||
      !/^\d*\.?\d*$/.test(parseFloat($(".sh_discount_value").val()))
    ) {
      $(".sh_discount_value").addClass("invalid_number");
      $(".sh_discount_value").val(" ");
      $(".sh_discount_value").focus();
    } else {
      var value = $(".sh_discount_value").val();
      value = !isNaN(value)
        ? value
        : isNaN(parseFloat(value))
          ? 0
          : formatFloat("" + value);
      if (
        document.getElementById("discount_fixed_radio") &&
        document.getElementById("discount_fixed_radio").checked
      ) {
        if (self.pos.is_global_discount) {
          var total_before = self.pos.get_order().get_total_with_tax();
          var orderlines = self.pos.get_order().get_orderlines();
          for (let each_order_line of orderlines) {
            each_order_line.set_discount(0);
          }
          var total_after = self.pos.get_order().get_total_with_tax();
          if (total_after != total_before) {
            value =
              parseFloat(value) +
              parseFloat((total_after - total_before).toFixed(2));
          }

          var percentage =
            (value / self.pos.get_order().get_total_with_tax()) * 100;
          for (let each_order_line of orderlines) {
            each_order_line.set_custom_discount(parseFloat(percentage));
          }
          self.pos.get_order().set_order_global_discount(value);
        } else {
          var selected_orderline = self.pos
            .get_order()
            .get_selected_orderline();
          if (selected_orderline) {
            if (selected_orderline.get_discount()) {
              var price = selected_orderline.get_display_price();
              var current_price = price - value;
              var discount =
                ((selected_orderline.price * selected_orderline.quantity -
                  current_price) /
                  (selected_orderline.price * selected_orderline.quantity)) *
                100;
              if (selected_orderline.get_fix_discount()) {
                selected_orderline.set_total_discount(
                  selected_orderline.get_total_discount() + parseFloat(value)
                );
                selected_orderline.set_fix_discount(
                  selected_orderline.get_fix_discount() + parseFloat(value)
                );
              } else {
                selected_orderline.set_total_discount(parseFloat(value));
                selected_orderline.set_fix_discount(parseFloat(value));
              }
              selected_orderline.set_global_discount(discount);
              selected_orderline.set_custom_discount(discount);
            } else {
              var apply_disc_percen =
                (value * 100) / selected_orderline.get_display_price();
              selected_orderline.set_total_discount(parseFloat(value));
              selected_orderline.set_fix_discount(parseFloat(value));
              selected_orderline.set_global_discount(apply_disc_percen);
              selected_orderline.set_custom_discount(apply_disc_percen);
              self.pos.get_order().set_order_global_discount(parseFloat(value));
            }
          }
        }
      }
      if (
        document.getElementById("discount_percentage_radio") &&
        document.getElementById("discount_percentage_radio").checked
      ) {
        if (self.pos.is_global_discount) {
          var orderlines = self.pos.get_order().get_orderlines();

          if (self.pos.get_order().get_order_global_discount()) {
            self.pos
              .get_order()
              .set_order_global_discount(
                self.pos.get_order().get_order_global_discount() +
                parseFloat(value)
              );
          } else {
            self.pos.get_order().set_order_global_discount(parseFloat(value));
          }
          debugger;
          var global_discount = 0
          for (let each_order_line of orderlines) {
            if (each_order_line.get_discount()) {
              var price = each_order_line.get_display_price();
              var current_price = price - (price * value) / 100;
              var discount =
                ((each_order_line.price * each_order_line.quantity -
                  current_price) /
                  (each_order_line.price * each_order_line.quantity)) *
                100;
              each_order_line.set_global_discount(discount);
              each_order_line.set_custom_discount(
                parseFloat(discount.toFixed(2))
              );
              each_order_line.set_total_discount(
                parseFloat(each_order_line.price) -
                parseFloat(each_order_line.get_display_price())
              );
              global_discount += current_price
            } else {
              var price = each_order_line.get_display_price();

              var current_price = price * value / 100;
              each_order_line.set_global_discount(parseFloat(value));
              each_order_line.set_custom_discount(parseFloat(value));
              each_order_line.set_total_discount(
                parseFloat(each_order_line.price) -
                parseFloat(each_order_line.get_display_price())
              );
              global_discount += current_price
            }
          }
          self.pos.get_order().set_order_global_discount(parseFloat(global_discount));
        } else {
          var selected_orderline = self.pos
            .get_order()
            .get_selected_orderline();
          if (selected_orderline) {
            if (selected_orderline.get_discount()) {
              var price = selected_orderline.get_display_price();

              var current_price = price - (price * value) / 100;
              var discount =
                ((selected_orderline.price * selected_orderline.quantity -
                  current_price) /
                  (selected_orderline.price * selected_orderline.quantity)) *
                100;
              selected_orderline.set_global_discount(discount);
              selected_orderline.set_custom_discount(discount);
              selected_orderline.set_total_discount(
                parseFloat(selected_orderline.price) -
                parseFloat(selected_orderline.get_display_price())
              );
            } else {
              var price = selected_orderline.get_display_price();

              var current_price = price * value / 100;

              selected_orderline.set_global_discount(parseFloat(value));
              selected_orderline.set_custom_discount(parseFloat(value));
              selected_orderline.set_total_discount(
                parseFloat(selected_orderline.price) -
                parseFloat(selected_orderline.get_display_price())
              );
              self.pos.get_order().set_order_global_discount(parseFloat(current_price));
            }
          }
        }
      }

      self.cancel();
    }
  }
}

/** @odoo-module */

import { Chrome } from "@point_of_sale/app/pos_app";
import { patch } from "@web/core/utils/patch";


patch(Chrome.prototype, {
    setup() {
        super.setup(...arguments)
document.addEventListener("keydown", (event) => {
    if(self && self.posmodel && self.posmodel.db){
        self.posmodel.db.keysPressed[event.key] = true;
    }
});

document.addEventListener("keyup", (event) => {
    if(self && self.posmodel && self.posmodel.db){
        delete self.posmodel.db.keysPressed[event.key];
    }
});

document.addEventListener("keydown", async(event) => {
    if (self && self.posmodel && self.posmodel.config && self.posmodel.config.sh_enable_shortcut) {
        self.posmodel.db.keysPressed[event.key] = true;
        self.posmodel.db.pressedKeyList = [];
        for (var key in self.posmodel.db.keysPressed) {
            if (self.posmodel.db.keysPressed[key]) {
                self.posmodel.db.pressedKeyList.push(key);
            }
        }
        if (self.posmodel.db.pressedKeyList.length > 0) {
            var pressed_key = "";
            for (var i = 0; i < self.posmodel.db.pressedKeyList.length > 0; i++) {
                if (self.posmodel.db.pressedKeyList[i]) {
                    if (pressed_key != "") {
                        pressed_key = pressed_key + "+" + self.posmodel.db.pressedKeyList[i];
                    } else {
                        pressed_key = self.posmodel.db.pressedKeyList[i];
                    }
                }
            };

            if ($(".payment-screen").is(":visible")) {
                if (self.posmodel.db.screen_by_key[pressed_key]) {
                    event.preventDefault();
                    if (self.posmodel.db.screen_by_key[pressed_key]) {
                        var payment_method = self.posmodel.payment_methods_by_id[self.posmodel.db.screen_by_key[pressed_key]];

                        if (payment_method) {
                            self.posmodel.get_order().add_paymentline(payment_method);
                        }
                    }
                }
            }
            for (var key in self.posmodel.db.key_screen_by_id) {
                if (self.posmodel.db.key_screen_by_id[key] == pressed_key) {
                    if (!$(".border-0 mx-2").is(":focus") && !$('textarea').is(":focus") && !$('input').is(":focus")) {
                        if (key == "select_up_orderline") {
                            event.preventDefault();
                            event.stopPropagation();
                            if ($(".product-screen").is(":visible")) {
                                $(document).find("div.product-screen .order-container li.selected").prev("li.orderline").trigger("click");
                            }
                        } else if (key == "select_down_orderline") {
                            event.preventDefault();
                            event.stopPropagation();
                            if ($(".product-screen").is(":visible")) {
                                $(document).find("div.product-screen .order-container li.selected").next("li.orderline").trigger("click");
                            }
                        } else if (key == "select_up_customer") {
                            if ($(document).find("table.partner-list tbody.partner-list-contents tr.highlight").length > 0) {
                                $(document).find("table.partner-list tbody.partner-list-contents tr.highlight").prev("tr.partner-line").click();
                            } else {
                                var clientLineLength = $(document).find("table.partner-list tbody.partner-list-contents tr.partner-line").length;
                                if (clientLineLength > 0) {
                                    $($(document).find("table.partner-list tbody.partner-list-contents tr.partner-line")[clientLineLength - 1]).click();
                                }
                            }
                        } else if (key == "select_down_customer") {
                            if ($(document).find("table.partner-list tbody.partner-list-contents tr.highlight").length > 0) {
                                $(document).find("table.partner-list tbody.partner-list-contents tr.highlight").next("tr.partner-line").click();
                            } else {
                                var clientLineLength = $(document).find("table.partner-list tbody.partner-list-contents tr.partner-line").length;
                                if (clientLineLength > 0) {
                                    $($(document).find("table.partner-list tbody.partner-list-contents tr.partner-line")[0]).click();
                                }
                            }
                        } else if (key == "go_payment_screen") {
                            if(self.posmodel.config.disable_payment_id && self.posmodel.config.disable_payment_id[0] && self.posmodel.user.groups_id.indexOf(self.posmodel.config.disable_payment_id[0]) == -1){
                                event.preventDefault();
                                event.stopPropagation();
                                if ($(".product-screen").is(":visible")) {
                                   await self.posmodel.showScreen("PaymentScreen")
                                    self.posmodel.db.keysPressed = {};
                                   await self.posmodel.get_order().clean_empty_paymentlines()
                                }
                            }
                        } else if (key == "go_customer_Screen") {
                            if(self.posmodel.config.group_select_customer && self.posmodel.config.group_select_customer[0] && self.posmodel.user.groups_id.indexOf(self.posmodel.config.group_select_customer[0]) == -1){
                                event.preventDefault();
                                event.stopPropagation();
                                if ($(".product-screen").is(":visible")) {
                                    $('.set-partner').click()
                                }
                                if ($(".payment-screen").is(":visible")) {
                                    $('.partner-button').click()
                                }

                            }
                        } else if (key == "validate_order") {
                            event.preventDefault();
                            event.stopPropagation();
                            if ($(".payment-screen").is(":visible")) {
                                if ($(".next").hasClass("highlight")) {
                                    $(".next.highlight").trigger("click");
                                }
                            }
                        } else if (key == "next_order") {
                            event.preventDefault();
                            event.stopPropagation();
                            if ($(".receipt-screen").is(":visible")) {
                                if ($(".next").hasClass("highlight")) {
                                    $(".next.highlight").trigger("click");
                                }
                            }
                        } else if (key == "go_to_previous_screen") {
                            event.preventDefault();
                            event.stopPropagation();
                            if (!$(".product-screen").is(":visible") && !$(".receipt-screen").is(":visible") && !$(".ticket-screen").is(":visible")) {
                                $(".back").trigger("click");
                            }
                            if ($(".ticket-screen").is(":visible")) {
                                $(".discard").trigger("click");
                            }
                        } else if (key == "select_quantity_mode") {
                            if ($(".product-screen").is(":visible")) {
                                let btn =  $("button:contains('Qty')")
                                btn.click();
                            }
                        } else if (key == "select_discount_mode") {
                            if ($(".product-screen").is(":visible")) {
                                let btn =  $("button:contains('% Disc')")
                                btn.click();
                            }
                        } else if (key == "select_price_mode") {
                            if ($(".product-screen").is(":visible")) {
                                let btn =  $("button:contains('Price')")
                                btn.click();
                            }
                        } else if (key == "search_product") {
                            event.preventDefault();
                            event.stopPropagation();
                            if ($(".product-screen").is(":visible")) {
                                var inputElement = $('input:input[placeholder="Search products..."]');
                                inputElement.focus();
                                // $(".search-clear-partner").click();
                            }
                        } else if (key == "add_new_order") {
                            event.preventDefault();
                            event.stopPropagation();
                            if ($(".ticket-screen").is(":visible")) {
                                $(".highlight").trigger("click");
                            }
                        } else if (key == "destroy_current_order") {
                            event.preventDefault();
                            event.stopPropagation();
                            $(document).find("div.ticket-screen div.orders div.order-row.highlight div.delete-button").click();
                        } else if (key == "delete_orderline") {
                            if ($(".product-screen").is(":visible")) {
                                if (self.posmodel.get_order().get_selected_orderline()) {
                                    // setTimeout(function () {
                                    self.posmodel.get_order().removeOrderline(self.posmodel.get_order().get_selected_orderline());
                                    // }, 150);
                                }
                            }
                        } else if (key == "search_customer") {
                            event.preventDefault();
                            event.stopPropagation();
                            if ($(".partnerlist-screen").is(":visible")) {
                                $(".search-bar-container.sb-partner input").focus();
                            }
                        } else if (key == "set_customer") {
                            event.preventDefault();
                            event.stopPropagation();
                            if ($(".partnerlist-screen").is(":visible")) {
                                if ($(document).find("table.partner-list tbody.partner-list-contents tr.partner-line.highlight")) {
                                    $(document).find("table.partner-list tbody.partner-list-contents tr.partner-line.highlight").click();
                                }
                            }
                        } else if (key == "create_customer") {
                            event.preventDefault();
                            event.stopPropagation();
                            if ($(".partnerlist-screen").is(":visible")) {
                                $(document).find("div.top-content button.new-customer").click();
                                setTimeout(function () {
                                    $(document).find("input.partner-name").focus();
                                }, 150);
                            }
                        } else if (key == "save_customer") {
                            if (!$(document.activeElement).is(":focus")) {
                                event.preventDefault();
                                event.stopPropagation();
                                if ($(".partnerlist-screen").is(":visible")) {
                                    let btn =  $("span:contains('Save')")
                                    btn.click();
                                }
                            }
                        } else if (key == "edit_customer") {
                            if (!$(document.activeElement).is(":focus")) {
                                event.preventDefault();
                                event.stopPropagation();
                                if ($(".partnerlist-screen").is(":visible")) {
                                    $(document).find("table.partner-list tbody.partner-list-contents tr.partner-line.highlight .edit-partner-button").click();
                                    setTimeout(function () {
                                        $(document).find("section.full-content section.partner-details input.partner-name").focus();
                                    }, 150);
                                }
                            }
                        } else if (key == "select_up_payment_line") {
                            if ($(".payment-screen").is(":visible")) {
                                if ($(document).find("div.payment-screen div.paymentline.selected").length > 0) {
                                    var highlighted_payment_line = $(document).find("div.payment-screen  div.paymentline.selected");
                                    if (highlighted_payment_line.prev("div.paymentline").length > 0) {
                                        $(document).find("div.payment-screen  div.paymentline.selected").prev("div.paymentline").addClass("selected");
                                        highlighted_payment_line.removeClass("selected");
                                    }
                                } else {
                                    var orderLineLength = $(document).find("div.payment-screen  div.paymentline.selected").length;
                                    if (orderLineLength > 0) {
                                        $($(document).find("div.payment-screen  div.paymentline")[orderLineLength - 1]).addClass("selected");
                                    }
                                }
                            }
                        } else if (key == "select_down_payment_line") {
                            if ($(".payment-screen").is(":visible")) {
                                if ($(document).find("div.payment-screen  div.paymentline.selected").length > 0) {
                                    var highlighted_payment_line = $(document).find("div.payment-screen  div.paymentline.selected");
                                    if (highlighted_payment_line.next("div.paymentline").length > 0) {
                                        $(document).find("div.payment-screen  div.paymentline.selected").next("div.paymentline").click();
                                        highlighted_payment_line.removeClass("selected");
                                    }
                                } else {
                                    var orderLineLength = $(document).find("div.payment-screen  div.paymentline.selected").length;
                                    if (orderLineLength > 0) {
                                        $($(document).find("div.payment-screen  div.paymentline")[0]).click();
                                    }
                                }
                            }
                        } else if (key == "delete_payment_line") {
                            if ($(".payment-screen").is(":visible")) {
                                setTimeout(function () {
                                    event.preventDefault();
                                    var elem = $(document).find("div.payment-screen  div.left-content div.paymentline.selected");

                                    if (elem.next("div.paymentline").length > 0) {
                                        $(document).find("div.payment-screen  div.left-content div.paymentline.selected button.delete-button").trigger("click");
                                        elem.next("div.paymentline").click();
                                        self.posmodel.db.keysPressed = {};
                                    } else {
                                        $(document).find("div.payment-screen  div.paymentline.selected button.delete-button").trigger("click");
                                        if (elem.prev("div.paymentline").length > 0) {
                                            elem.prev("div.paymentline").click();
                                            self.posmodel.db.keysPressed = {};
                                        }
                                    }
                                }, 200);
                            }
                        } else if (key == "+10") {
                            if ($(".payment-screen").is(":visible")) {
                                let btn =  $("button:contains('+10')")
                                btn.click();
                            }
                        } else if (key == "+20") {
                            if ($(".payment-screen").is(":visible")) {
                                let btn =  $("button:contains('+20')")
                                btn.click();
                            }
                        } else if (key == "+50") {
                            event.preventDefault();
                            event.stopPropagation();
                            if ($(".payment-screen").is(":visible")) {
                                let btn =  $("button:contains('+50')")
                                btn.click();
                            }
                        } else if (key == "go_order_Screen") {
                            if ($(".payment-screen").is(":visible") || $(".product-screen").is(":visible")) {
                                let btn =  $("button:contains('Refund')")
                                btn.click();
                            }
                        } else if (key == "search_order") {
                            event.preventDefault();
                            event.stopPropagation();
                            if ($(".ticket-screen").is(":visible")) {
                                $(".search input").focus();
                            }
                        } else if (key == "select_up_order") {
                            if ($(".ticket-screen").is(":visible")) {
                                if ($(document).find("div.ticket-screen div.orders div.order-row.highlight").length > 0) {
                                    var highlighted_order = $(document).find("div.ticket-screen div.orders div.order-row.highlight");
                                    if (highlighted_order.prev("div.order-row").length > 0) {
                                        $(document).find("div.ticket-screen div.orders div.order-row.highlight").prev("div.order-row").addClass("highlight");
                                        highlighted_order.removeClass("highlight");
                                    }
                                } else {
                                    var orderLineLength = $(document).find("div.ticket-screen div.orders div.order-row").length;
                                    if (orderLineLength > 0) {
                                        $($(document).find("div.ticket-screen div.orders div.order-row")[orderLineLength - 1]).addClass("highlight");
                                    }
                                }
                            }
                        } else if (key == "select_down_order") {
                            if ($(".ticket-screen").is(":visible")) {
                                if ($(document).find("div.ticket-screen div.orders div.order-row.highlight").length > 0) {
                                    var highlighted_order = $(document).find("div.ticket-screen div.orders div.order-row.highlight");
                                    if (highlighted_order.next("div.order-row").length > 0) {
                                        $(document).find("div.ticket-screen div.orders div.order-row.highlight").next("div.order-row").addClass("highlight");
                                        highlighted_order.removeClass("highlight");
                                    }
                                } else {
                                    var orderLineLength = $(document).find("div.ticket-screen div.orders div.order-row").length;
                                    if (orderLineLength > 0) {
                                        $($(document).find("div.ticket-screen div.orders div.order-row")[0]).addClass("highlight");
                                    }
                                }
                            }
                        } else if (key == "select_order") {
                            if ($(".ticket-screen").is(":visible")) {
                                if ($(document).find("div.ticket-screen div.orders div.order-row.highlight").length > 0) {
                                    $(document).find("div.ticket-screen div.orders div.order-row.highlight").click();
                                }
                            }
                        }
                    }
                }
            }
        }
    }
});

document.addEventListener("keyup", (event) => {
    if(self && self.posmodel && self.posmodel.db){
        self.posmodel.db.keysPressed = {};
        delete self.posmodel.db.keysPressed[event.key];
    }
});


    }
})
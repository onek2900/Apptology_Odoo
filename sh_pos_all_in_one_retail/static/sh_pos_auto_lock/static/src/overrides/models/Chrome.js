/** @odoo-module */

import { Chrome } from "@point_of_sale/app/pos_app";
import { patch } from "@web/core/utils/patch";
import { Component, onMounted } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { NumberPopup } from "@point_of_sale/app/utils/input_popups/number_popup";
import { _t } from "@web/core/l10n/translation";
import { SelectionPopup } from "@point_of_sale/app/utils/input_popups/selection_popup";

patch(Chrome.prototype, {
    setup(){
        super.setup(...arguments)
        this.popup = useService("popup");
        this.sh_timer = false
        this.sh_start()
    },
    async askPin(employee) {
        const { confirmed, payload: inputPin } = await this.popup.add(NumberPopup,  {
            isPassword: true,
            title: "Password ?",
            startingValue: null,
        });

        if (!confirmed){
            
            if(this.pos.is_timer_screen){
                $(".pos").before('<div class="blur_screen"><h3>Tap to unlock...</h3></div>');
            }
            return false;
        } 
        if (employee.pin === Sha1.hash(inputPin)) {
            this.pos.set_cashier(employee);
            this.pos.is_timer_screen = false;
            return employee;
        } else {

            alert("Incorrect Password")
            if(this.pos.is_timer_screen){
                $(".pos").before('<div class="blur_screen"><h3>Tap to unlock...</h3></div>');
            }
            return false;
        }
    },
    sh_start() {
        var self = this;
        if (this.pos.config.sh_enable_auto_lock) {
            var set_logout_interval = function (time) {
                time = time || self.pos.config.sh_lock_timer * 1000;
                if (time) {
                    self.sh_timer = setTimeout(function () {
                        self.pos.is_timer_screen = true
                        $(".pos").before('<div class="blur_screen"><h3>Tap to unlock...</h3></div>');
                    }, time);
                }
            };
        }
        if (this.pos.config.sh_enable_auto_lock && this.pos.config.sh_lock_timer) {
            $(document).on("click", async function (event) {
                if (self.pos.config.sh_enable_auto_lock && self.pos.config.sh_lock_timer) {
                    clearTimeout(self.sh_timer);
                    set_logout_interval();
                    if ($(".blur_screen").length > 0) {
                        if(!self.pos.is_not_remove_screen){
                            $(".blur_screen").remove();
                        }else{
                            self.pos.is_not_remove_screen = false
                        }
                        const current = Component.current;
                        if (self.pos.config.module_pos_hr) {
                            const list = self.pos.employees.map((employee) => {
                                if (employee.name == self.pos.get_cashier().name) {
                                    return {
                                        id: employee.id,
                                        item: employee,
                                        label: employee.name,
                                        isSelected: true,
                                    };
                                } else {
                                    return {
                                        id: employee.id,
                                        item: employee,
                                        label: employee.name,
                                        isSelected: false,
                                    };
                                }
                            });

                            const { confirmed, payload: selectedCashier } = await self.popup.add(
                                SelectionPopup, {
                                title: "Change Cashier",
                                list: list,
                            });

                            if (!confirmed) {
                                if(self.pos.is_timer_screen){
                                    self.pos.is_not_remove_screen = true
                                    event.preventDefault()
                                    $(".pos").before('<div class="blur_screen"><h3>Tap to unlock...</h3></div>');
                                }
                                return false;
                            }
                            if (!selectedCashier.pin) {
                                self.pos.set_cashier(selectedCashier);
                                self.pos.is_timer_screen = false;
                                return selectedCashier;
                            } else {
                                return self.askPin(selectedCashier);
                            }
                        }else{
                            self.pos.is_timer_screen = false;
                        }
                    }
                }
            });
            set_logout_interval();
        }

}
});

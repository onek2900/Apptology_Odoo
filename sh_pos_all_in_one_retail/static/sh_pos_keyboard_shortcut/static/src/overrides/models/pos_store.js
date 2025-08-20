/** @odoo-module */

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { patch } from "@web/core/utils/patch";

patch(PosStore.prototype, {
    // async setup(env, { popup, orm, number_buffer, hardware_proxy, barcode_reader, ui }) {
    //     await super.setup(env, { popup, orm, number_buffer, hardware_proxy, barcode_reader, ui });
    //     this.db.all_key = [];
    //     this.db.all_key_screen = [];
    //     this.db.key_screen_by_id = {};
    //     this.db.key_by_id = {};
    //     this.db.screen_by_key = {};
    //     this.db.keysPressed = {};
    //     this.db.pressedKeyList = [];
    //     this.db.key_screen_by_grp = {};
    //     this.db.key_payment_screen_by_grp = {};
    //     this.db.temp_key_by_id = {};
    // },
    async _processData(loadedData) {
        await super._processData(loadedData);
        this.db.all_key = [];
        this.db.all_key_screen = [];
        this.db.key_screen_by_id = {};
        this.db.key_by_id = {};
        this.db.screen_by_key = {};
        this.db.keysPressed = {};
        this.db.pressedKeyList = [];
        this.db.key_screen_by_grp = {};
        this.db.key_payment_screen_by_grp = {};
        this.db.temp_key_by_id = {};
        this.keyboard_keys_temp = loadedData['sh.keyboard.key.temp'];
        await this.loadKeyboardKeysTemp(loadedData['sh.keyboard.key.temp']);
        this.keyboard_keys = loadedData['sh.pos.keyboard.shortcut'];
        this.loadKeyboardKeys(this.keyboard_keys);
    },
    loadKeyboardKeysTemp(keyboard_keys_temp){
        var self = this
        if(keyboard_keys_temp && keyboard_keys_temp.length > 0){
            self.db.all_key = keyboard_keys_temp;
            for(let each_key of Object.values(keyboard_keys_temp)){
                if (each_key && each_key.name) {
                    self.db.temp_key_by_id[each_key.id] = each_key;
                }
            };
        }
    },
    loadKeyboardKeys(keyboard_keys){
        var self = this
        if(keyboard_keys && keyboard_keys.length > 0){
            self.db.all_key_screen = keyboard_keys;
            for(let each_key_data of keyboard_keys){
                var key_combine = "";
                for(let each_key of each_key_data['sh_key_ids']){
                    if(self.db.temp_key_by_id[each_key]){
                        if (key_combine != "") {
                            key_combine = key_combine + "+" + self.db.temp_key_by_id[each_key]["name"];
                        } else {
                            key_combine = self.db.temp_key_by_id[each_key]["name"];
                        }
                    }
                };
                if (each_key_data.payment_method_id && each_key_data.payment_method_id) {
                    self.db.screen_by_key[key_combine] = each_key_data["payment_method_id"][0];

                    self.db.key_screen_by_id[each_key_data["payment_method_id"]] = key_combine;
                    if (each_key_data["sh_payment_shortcut_screen_type"]) {
                        if (self.db.key_payment_screen_by_grp[each_key_data["sh_payment_shortcut_screen_type"]]) {
                            self.db.key_payment_screen_by_grp[each_key_data["sh_payment_shortcut_screen_type"]].push(each_key_data["payment_method_id"]);
                        } else {
                            self.db.key_payment_screen_by_grp[each_key_data["sh_payment_shortcut_screen_type"]] = [each_key_data["payment_method_id"]];
                        }
                    }
                } else {
                    self.db.key_screen_by_id[each_key_data["sh_shortcut_screen"]] = key_combine;
                    if (each_key_data.sh_shortcut_screen_type) {
                        if (self.db.key_screen_by_grp[each_key_data.sh_shortcut_screen_type]) {
                            self.db.key_screen_by_grp[each_key_data.sh_shortcut_screen_type].push(each_key_data["sh_shortcut_screen"]);
                        } else {
                            self.db.key_screen_by_grp[each_key_data.sh_shortcut_screen_type] = [each_key_data["sh_shortcut_screen"]];
                        }
                        
                    }
                }
            };
        }
    }
});


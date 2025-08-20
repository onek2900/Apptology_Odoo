/** @odoo-module **/
/* global waitIndexDb */

import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { session } from "@web/session";
import { onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { SwitchCompanyItem } from "@web/webclient/switch_company_menu/switch_company_menu";
import { patch } from "@web/core/utils/patch";
const { Component } = owl;


patch(SwitchCompanyItem.prototype, {
  get isCompanySelected() {
    localStorage.setItem('Products', 'notloaded')
    return super.isCompanySelected
  }
})


export class UserNotificationMenu extends Component {
  setup() {
    this.rpc = useService("rpc");
    this.busService = this.env.services.bus_service;
    this.action = useService("action");
    onWillStart(this.onWillStart);
  }

  async onWillStart() {
    this.busService.addEventListener(
      "notification",
      ({ detail: notifications }) => {
        for(let notif of notifications){
          var { type, payload } = notif;
          if (type == 'product_update'){
            const indexedDB = waitIndexDb(function () {
              resolve();
            });
            
            indexedDB.save_data('Products', [payload[0]])
          }
        }
      }
    );
  }
}
UserNotificationMenu.template = "mail.systray.UserNotificationMenu";

export const systrayItem = {
  Component: UserNotificationMenu,
};

registry.category("systray").add("UserNotificationMenu", systrayItem);

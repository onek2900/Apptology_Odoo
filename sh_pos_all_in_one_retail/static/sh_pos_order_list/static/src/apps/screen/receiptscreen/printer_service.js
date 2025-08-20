/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { PrinterService } from "@point_of_sale/app/printer/printer_service";

patch(PrinterService.prototype, {
  async print(component, props, options) {
      this.pos.get_order().is_reciptScreen =  true
      await super.print(...arguments)
  } 
});

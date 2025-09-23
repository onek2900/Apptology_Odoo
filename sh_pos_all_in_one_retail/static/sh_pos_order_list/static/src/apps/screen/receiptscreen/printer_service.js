/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { PrinterService } from "@point_of_sale/app/printer/printer_service";

patch(PrinterService.prototype, {
  async print(component, props, options) {
      await super.print(...arguments)
  } 
});

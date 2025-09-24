/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { PrinterService } from "@point_of_sale/app/printer/printer_service";

patch(PrinterService.prototype, {
  async print(component, props, options) {
      try {
        const order = this.pos && typeof this.pos.get_order === 'function' ? this.pos.get_order() : null;
        if (order) {
          order.is_reciptScreen = true;
        }
      } catch (e) {
        // Silently ignore if no active order context (e.g., external printing)
      }
      await super.print(...arguments)
  } 
});

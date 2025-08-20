/** @odoo-module */

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { patch } from "@web/core/utils/patch";

patch(PosStore.prototype, {
  async _processData(loadedData) {
    await super._processData(...arguments);
    var self = this;
    self.suggestions = loadedData["product.suggestion"] || [];
    self.sh_uom_line = loadedData["sh.uom.line"] || [];

    self.suggestions = JSON.parse(JSON.stringify(self.suggestions));
    self.suggestion = {};
    self.sh_uom_line_by_id = {}
    
    for (let sh_uom_line of self.sh_uom_line) {
      self.sh_uom_line_by_id[sh_uom_line.id] = sh_uom_line;
    }

    for (let suggestion of self.suggestions) {
      self.suggestion[suggestion.id] = suggestion;
    }
  },
});

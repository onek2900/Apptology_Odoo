/** @odoo-module */

import { Orderline, Order } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";


patch(Orderline.prototype, {
  getDisplayData() {
    var res = super.getDisplayData()
    res['default_code'] = this.get_product().default_code
    return res
  }
});

patch(Order.prototype, {
  export_for_printing() {
    var receipt = super.export_for_printing(...arguments);
    // Create qr code 
    if (this.pos.config.sh_pos_receipt_bacode_qr && this.pos.config.sh_pos_receipt_barcode_qr_selection == 'qr'  ) {
      const codeWriter = new window.ZXing.BrowserQRCodeSvgWriter();
      const qr_values = this.name.split(' ')[1];
      const qr_code_svg = new XMLSerializer().serializeToString(
        codeWriter.write(qr_values, 120, 120)
      );
      receipt.sh_link_qr_code = "data:image/svg+xml;base64," + window.btoa(qr_code_svg);
    }
    // [create barcode]
    var createElement = document.createElement('img')
    JsBarcode(createElement).options({ font: "OCR-B", displayValue: false })
      .CODE128(this.name.split(' ')[1], { fontSize: 18, textMargin: 0, height: 70 })
      .blank(0)
      .render();

    receipt.sh_order_barcode = createElement.src
    return receipt;
  },
});

patch(PosStore.prototype, {
  getReceiptHeaderData() {
    var data = super.getReceiptHeaderData(...arguments);
    data['sh_created_seq'] = this.get_order().sh_created_seq || false
    return data
  }
})
// /** @odoo-module */

// import { patch } from "@web/core/utils/patch";
// import { PosPrinterService } from "@point_of_sale/app/printer/printer_service";
// import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";

// patch(PosPrinterService.prototype, {
//   setup() {
//     super.setup(...arguments);
//   },
//   async printWeb() {
//     try {
//       setTimeout(() => {
//         window.print();
//       }, 100);
//       return true;
//     } catch (err) {
//       await this.popup.add(ErrorPopup, {
//         title: _t("Printing is not supported on some browsers"),
//         body: _t(
//           "Printing is not supported on some browsers due to no default printing protocol " +
//             "is available. It is possible to print your tickets by making use of an IoT Box."
//         ),
//       });
//       return false;
//     }
//   },
// });

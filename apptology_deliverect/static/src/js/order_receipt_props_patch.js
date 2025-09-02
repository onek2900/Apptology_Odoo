/** @odoo-module */

// Allow external modules to pass an optional 'receipt_type' prop
// to the built-in OrderReceipt component (used by some receipt
// size/format extensions). Without this, Owl raises an unknown
// prop validation error when templates add the attribute.

import { OrderReceipt } from "@point_of_sale/app/screens/receipt_screen/receipt/order_receipt";

if (OrderReceipt && OrderReceipt.props) {
    OrderReceipt.props = {
        ...OrderReceipt.props,
        receipt_type: { type: String, optional: true },
    };
}


/** @odoo-module */
import { register_payment_method } from "@point_of_sale/app/store/pos_store";
import { PaymentMoneris } from "@apptology_pos_moneris/app/payment_moneris";

register_payment_method("moneris", PaymentMoneris);

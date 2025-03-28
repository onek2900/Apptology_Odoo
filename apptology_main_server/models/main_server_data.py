from odoo import models, fields, api
import re

class MainServerData(models.Model):
    _name = 'main.server.data'
    _description = 'Main Server Data'
    _rec_name = "registration_url"
    _sql_constraints = [
        ('pos_id_unique', 'UNIQUE(pos_id)', 'POS ID must be unique'),
    ]

    registration_url = fields.Char(string='Registration Url',required=True)
    account_id = fields.Char(string='Account ID')
    pos_id = fields.Char(string='POS ID',required=True)
    order_sync_url = fields.Char(string='Order Sync Url', compute='_compute_order_url',store=True)
    product_sync_url = fields.Char(string='Product Sync Url', compute='_compute_product_url',store=True)
    customer_pos_status = fields.Selection([('fail', 'Failed'),('success','Success')])

    @api.depends('registration_url', 'pos_id')
    def _compute_order_url(self):
        for rec in self:
            print(rec)
            rec.order_sync_url=""
            print(rec.registration_url,rec.pos_id)
            if rec.registration_url and rec.pos_id:
                rec.order_sync_url = re.sub(r"/pos/register$", f"/pos/orders/{rec.pos_id}", rec.registration_url)
                print(rec.order_sync_url)

    @api.depends('registration_url', 'pos_id')
    def _compute_product_url(self):
        for rec in self:
            rec.product_sync_url=""
            if rec.registration_url and rec.pos_id:
                rec.product_sync_url = re.sub(r"/pos/register$", f"/pos/products/{rec.pos_id}", rec.registration_url)

    # @http.route('/deliverect/pos/register', type='json', methods=['POST'], auth="none", csrf=False)
    # def register_pos(self):
    #     try:
    #         _logger.info(f"Received Registration Data")
    #         data = json.loads(request.httprequest.data)
    #         print(data)
    #         pos_id = data.get('externalLocationId')
    #         pos_configuration = request.env['pos.config'].sudo().search([('pos_id','=',pos_id)],limit=1)
    #         pos_configuration.write({
    #             'account_id': data.get('accountId'),
    #             'location_id': data.get('locationId'),
    #         })
    #         is_channel_present = pos_configuration.create_customers_channel()
    #         request.env['deliverect.allergens'].sudo().update_allergens()
    #         if is_channel_present['params']['title'] == 'Failure':
    #             pos_configuration.write({
    #                 'status_message': f"{is_channel_present['params']['message']}",
    #             })
    #             return {
    #                 "status": "fail",
    #                 "message": is_channel_present['params']['message'],
    #             }
    #         else:
    #             pos_configuration.write({
    #                 'status_message': f"POS Registration Successful"
    #             })
    #             return {
    #                 "status": "success",
    #                 "message": "Webhook received successfully",
    #                 "received_data": data
    #             }
    #
    #     except Exception as e:
    #         _logger.error(f"Error processing webhook: {str(e)}")
    #         return {
    #             "status": "error",
    #             "message": str(e)
    #         }
# -*- coding: utf-8 -*-
import base64
import os
from odoo.http import request, route, Controller



class PosImageReceipt(Controller):

    @route('/save/order_receipt_image', type='json', auth="user", methods=['POST'])
    def save_order_receipt_image(self, tracking_number, image_data, name):

        try:
            directory_path = f'/var/tmp/{name}'
            os.makedirs(directory_path, exist_ok=True)
            save_path = os.path.join(directory_path, f'order_receipt_{tracking_number}.png')
            image_bytes = base64.b64decode(image_data)

            with open(save_path, 'wb') as f:
                f.write(image_bytes)

            return {'status': 'success', 'message': 'Image saved successfully'}
        except Exception as e:
            return {'status': 'failed', 'message': 'Image saving failed', 'error': str(e)}


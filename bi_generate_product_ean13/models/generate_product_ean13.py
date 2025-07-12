# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api
from datetime import datetime
import random
from barcode import EAN13
try:
	from barcode.writer import ImageWriter
except ImportError:
	ImageWriter = None  # lint:ok
import base64
import os


class biproductgeneratebarcodemanually(models.TransientModel):
	_name = 'bi.product.generate.barcode.manually'
	_description="Bi Product Generate Barcode Manually"

	generate_type = fields.Selection([('date', 'Generate Barcode EAN13 (Using Today Date)'),
										('random', 'Generate Barcode EAN13 (Using Random Number)')],string='Barcode Generate Option',default='date')
	


	def generate_barcode_manually(self):
		for record in self.env['product.product'].browse(self._context.get('active_id')):
			if self.generate_type == 'date':
				bcode = self.env['barcode.nomenclature'].sanitize_ean("%s%s" % (record.id, datetime.now().strftime("%d%m%y%H%M")))
			else:
				number_random = int("%0.13d" % random.randint(0,999999999999))
				bcode = self.env['barcode.nomenclature'].sanitize_ean("%s" % (number_random))
			record.write({'barcode':bcode})
			if ImageWriter != None:
				ean = EAN13(bcode, writer=ImageWriter())
				if os.path.exists("/tmp"):
					filename = ean.save('/tmp/ean13')
				else:
					filename = ean.save('ean13')

				f = open(filename, 'rb')
				jpgdata = f.read()
				imgdata = base64.encodebytes(jpgdata)
				record.write({'barcode_img':imgdata})
				os.remove(filename)
		return True
		

class bi_generate_product_barcode(models.TransientModel):
	_name = 'bi.product.generate.barcode'
	_description='Bi Product Generate Barcode'

	overwrite= fields.Boolean(string="Overwrite Exists Ean13")
	generate_type = fields.Selection([('date', 'Generate Barcode EAN13 (Using Today Date)'),
										('random', 'Generate Barcode EAN13 (Using Random Number)')],string='Barcode Generate Option',default='date')


	def generate_barcode(self):
		for record in self.env['product.product'].browse(self._context.get('active_ids')):
			if not self.overwrite and record.barcode:
				continue
			
			if self.generate_type == 'date':
				bcode = self.env['barcode.nomenclature'].sanitize_ean("%s%s" % (record.id, datetime.now().strftime("%d%m%y%H%M")))
			else:
				number_random = int("%0.13d" % random.randint(0,999999999999))
				bcode = self.env['barcode.nomenclature'].sanitize_ean("%s" % (number_random))
			ean = EAN13(bcode, writer=ImageWriter())
			if os.path.exists("/tmp"):
				filename = ean.save('/tmp/ean13')
			else:
				filename = ean.save('ean13')
			f = open(filename, 'rb')
			jpgdata = f.read()
			imgdata = base64.encodebytes(jpgdata)
			record.write({'barcode':bcode,
						  'barcode_img': imgdata
			})

		return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

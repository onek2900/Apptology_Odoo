# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields, api
import base64


dict_theme_style = {
    "style_1":  {
        "primary_color": "#673ab7",
        "secondary_color": "#dee2e6",
        "button_style": "style_1",
        "product_style": "style_1",
        "sh_cart_position": "left_side",
        "sh_image_display_in_cart": True,
        "sh_action_button_position": 'bottom',
        "sh_mobile_start_screen": 'product_screen',
        "body_background_type": 'bg_color',
        "body_font_family": "Roboto",
        "body_background_color": '#ffffff',
        "sh_list_view_border": 'bordered',
        "sh_header_sticky": True,
        "sh_list_row_hover": True,
        "sh_hover_background_color": "#dee2e6",
        "sh_even_row_color": "#dee2e6",
        "sh_odd_row_color": "#FFFFFF",
        "form_element_style": "style_1",
        "sh_display_product_image_name": "image_name",
        "product_background_color": "#FFFFFF",
    },
    "style_2":  {
        "primary_color": "#43A047",
        "secondary_color": "#dee2e6",
        "button_style": "style_2",
        "product_style": "style_2",
        "sh_cart_position": "right_side",
        "sh_image_display_in_cart": True,
        "sh_action_button_position": 'right_side',
        "sh_mobile_start_screen": 'cart_screen',
        "body_background_type": 'bg_color',
        "body_background_color": '#f1f2f4',
        "sh_list_view_border": 'without_bordered',
        "sh_header_sticky": False,
        "sh_list_row_hover": False,
        "sh_even_row_color": "#dee2e6",
        "sh_odd_row_color": "#FFFFFF",
        "form_element_style": "style_2",
        "body_font_family": "KoHo",
        "sh_display_product_image_name": "image",
        "product_background_color": "#FFFFFF",
    },
    "style_3":  {
        "primary_color": "#C8385E",
        "secondary_color": "#ebebeb",
        "button_style": "style_3",
        "product_style": "style_3",
        "sh_cart_position": "left_side",
        "sh_image_display_in_cart": True,
        "sh_action_button_position": 'left_side',
        "sh_mobile_start_screen": 'product_screen',
        "body_background_type": 'bg_img',
        "body_background_color": '#ffffff',
        "sh_list_view_border": 'without_bordered',
        "sh_header_sticky": True,
        "sh_list_row_hover": True,
        "sh_hover_background_color": "#dee2e6",
        "sh_even_row_color": "#dee2e6",
        "sh_odd_row_color": "#FFFFFF",
        "form_element_style": "style_3",
        "body_font_family": "Lato",
        "sh_display_product_image_name": "product_name",
        "product_background_color": "#FFFFFF",
    },
    "style_4":  {
        # "primary_color": "#7978e9",
        # "secondary_color": "#f0f0f0",
        # "gradient_color": "#eea799",
         "primary_color": "#00c4cc",
        "secondary_color": "#f0f0f0",
        "gradient_color": "#7d2ae8",
        "button_style": "style_4",
        "product_style": "style_4",
        "sh_cart_position": "left_side",
        "sh_image_display_in_cart": True,
        "sh_action_button_position": 'bottom',
        "sh_mobile_start_screen": 'product_screen',
        "body_background_type": 'bg_color',
        "body_font_family": "Roboto",
        "body_background_color": '#e7e5e5',
        "sh_list_view_border": 'bordered',
        "sh_header_sticky": True,
        "sh_list_row_hover": True,
        "sh_hover_background_color": "#FFFFFF",
        "sh_even_row_color": "#dee2e6",
        "sh_odd_row_color": "#FFFFFF",
        # "sh_cart_total_sticky": True,
        "form_element_style": "style_4",
        "sh_display_product_image_name": "image_name",
        "product_background_color": "#FFFFFF",
    },
}


class sh_pos_theme_settings(models.Model):
    _name = "sh.pos.theme.settings"
    _description = "POS Theme Settings"

    name = fields.Char(string="POS Theme Settings",
                       default="POS Theme Settings")
    sh_cart_position = fields.Selection([('left_side', 'Left Side'), (
        'right_side', 'Right Side')], string="Cart Position", default='left_side', required=True)
    sh_image_display_in_cart = fields.Boolean(
        string="Is Image Display In Cart?")
    sh_action_button_position = fields.Selection([('left_side', 'Left Side'), ('bottom', 'Bottom'), (
        'right_side', 'Right Side')], string="Action Button Position", default='left_side', required=True)
    sh_mobile_start_screen = fields.Selection([('product_screen', 'Product Screen'), ('cart_screen', 'Cart Screen')], string="Startup Screen", default='product_screen', required=True)
    theme_style = fields.Selection([
        ("style_1", "Style 1"),
        ("style_2", "Style 2"),
        ("style_3", "Style 3"),
        ("style_4", "Style 4"),
    ], string="Theme Style", default="style_1", required=True)
    sh_pos_switch_view = fields.Boolean(string="Enable Product Switch View")
    sh_default_view = fields.Selection([('list_view', 'List View'), (
        'grid_view', 'Grid View')], default="grid_view", string="Default Product View")
    sh_display_product_name = fields.Boolean(
        string="Display Product Name", default="true")
    sh_display_product_image = fields.Boolean(
        string="Display Product Image", default="true")
    sh_display_product_price = fields.Boolean(
        string="Display Product Price", default="true")
    sh_display_product_code = fields.Boolean(
        string="Display Product Code", default="true")
    sh_display_product_type = fields.Boolean(string="Display Product Type")
    sh_display_product_onhand = fields.Boolean(
        string="Display Product On Hand", default="true")
    sh_display_product_forecasted = fields.Boolean(
        string="Display Product Forecasted Quantity")
    sh_display_product_uom = fields.Boolean(string="Display Product UOM")
    sh_product_image_size = fields.Selection([('small_size', 'Small Size'), ('medium_size', 'Medium Size'), (
        'large_size', 'Large Size')], default="medium_size", string="Image Size", required=True)
    primary_color = fields.Char(string="Primary Color")
    secondary_color = fields.Char(string="Secondary Color")
    product_style = fields.Selection([
        ("style_1", "Style 1"),
        ("style_2", "Style 2"),
        ("style_3", "Style 3"),
        ("style_4", "Style 4"),
    ], string="Product Box Style", default="style_1", required=True)
    button_style = fields.Selection([
        ("style_1", "Style 1"),
        ("style_2", "Style 2"),
        ("style_3", "Style 3"),
        ("style_4", "Style 4"),
    ], string="Button Style", default="style_1", required=True)
    body_background_type = fields.Selection([
        ("bg_color", "Color"),
        ("bg_img", "Image")
    ], string="Body Background Type", default="bg_color")

    body_background_color = fields.Char(string="Body Background Color")
    body_background_image = fields.Binary(string="Body Background Image")
    body_font_family = fields.Selection([
        ("Roboto", "Roboto"),
        ("Raleway", "Raleway"),
        ("Poppins", "Poppins"),
        ("Oxygen", "Oxygen"),
        ("OpenSans", "OpenSans"),
        ("KoHo", "KoHo"),
        ("Ubuntu", "Ubuntu"),
        ("Montserrat", "Montserrat"),
        ("Lato", "Lato"),
        ("custom_google_font", "Custom Google Font"),
    ], string="Body Font Family", required=True)

    body_google_font_family = fields.Char(string="Google Font Family")
    is_used_google_font = fields.Boolean(string="Is use google font?")
    sh_list_view_border = fields.Selection([
        ("bordered", "Bordered"),
        ("without_bordered", "Without Border")
    ], string="List View Border", default="bordered", required=True)
    sh_header_sticky = fields.Boolean(string=" Is Header Sticky?")
    sh_list_row_hover = fields.Boolean(string="Rows Hover?")
    sh_hover_background_color = fields.Char(string="Hover Background Color")
    sh_even_row_color = fields.Char(string="Even Row Color")
    sh_odd_row_color = fields.Char(string="Odd Row Color")
    gradient_color = fields.Char(string="Gradient color ")
    form_element_style = fields.Selection([
        ("style_1", "Style 1"),
        ("style_2", "Style 2"),
        ("style_3", "Style 3"),
        ("style_4", "Style 4"),
    ], string="Form Element Style", default="style_1", required=True)
    theme_logo = fields.Binary(string="Logo")
    sh_display_product_image_name = fields.Selection([
        ("image", "Image"),
        ("product_name", "Product Name"), ('image_name', 'Image + Name'),
    ], string="Product Detail", default="image_name", required=True)
    product_background_color = fields.Char(string="Product Background Color")
    display_cart_order_item_count = fields.Boolean("Display Cart Item Qty (Mobile)")
    display_product_cart_qty = fields.Boolean("Display Product Qty")

    @api.onchange('theme_style')
    def onchage_theme_style(self):
        if self and self.theme_style:
            selected_theme_style_dict = dict_theme_style.get(
                self.theme_style, False)
            if selected_theme_style_dict:
                self.update(selected_theme_style_dict)

    def write(self, vals):
        """
           Write theme settings data in a less file
        """

        res = super(sh_pos_theme_settings, self).write(vals)

        for rec in self:
            IrAttachment = self.env["ir.attachment"]
    
            URL = "/sh_pos_all_in_one_retail/static/sh_pos_theme_responsive/static/src/overrides/pos_theme_variables.scss"

            attachment = IrAttachment.sudo().search([
                ("url", "=", URL)
            ], limit=1)

            content = """     
                $sh_cart_position: %(sh_cart_position)s;
                $sh_image_display_in_cart: %(sh_image_display_in_cart)s;
                $sh_action_button_position: %(sh_action_button_position)s;
                $sh_mobile_start_screen: %(sh_mobile_start_screen)s;
                $sh_pos_theme_style: %(theme_style)s;
                $sh_pos_primary_color: %(primary_color)s;
                $sh_pos_secondary_color: %(secondary_color)s;
                $sh_pos_gradient_color: %(gradient_color)s;
                $sh_pos_product_style: %(product_style)s;
                $sh_pos_button_style: %(button_style)s;
                $sh_pos_body_background_type: %(body_background_type)s;
                $sh_pos_body_background_color: %(body_background_color)s;
                $sh_pos_body_background_image: %(body_background_image)s;
                $sh_pos_body_font_family: %(body_font_family)s;
                $sh_pos_body_google_font_family: %(body_google_font_family)s;
                $sh_pos_is_used_google_font: %(is_used_google_font)s;
                $sh_list_view_border: %(sh_list_view_border)s;
                $sh_list_row_hover: %(sh_list_row_hover)s;
                $sh_hover_background_color: %(sh_hover_background_color)s;
                $sh_even_row_color: %(sh_even_row_color)s;
                $sh_odd_row_color: %(sh_odd_row_color)s;
                $sh_header_sticky: %(sh_header_sticky)s;
                
                $sh_form_element_style: %(form_element_style)s;
                $sh_display_product_image_name: %(sh_display_product_image_name)s;
                $product_background_color: %(product_background_color)s;
            """ % {
                "sh_cart_position": rec.sh_cart_position,
                "sh_image_display_in_cart": rec.sh_image_display_in_cart,
                "sh_action_button_position": rec.sh_action_button_position,
                "sh_mobile_start_screen": rec.sh_mobile_start_screen,
                "theme_style": rec.theme_style,
                "primary_color": rec.primary_color,
                "secondary_color": rec.secondary_color,
                "gradient_color": rec.gradient_color,
                "product_style": rec.product_style,
                "button_style": rec.button_style,
                "body_background_type": rec.body_background_type,
                "body_background_color": rec.body_background_color,
                "body_background_image": rec.body_background_image,
                "body_font_family": rec.body_font_family,
                "body_google_font_family": rec.body_google_font_family,
                "is_used_google_font": rec.is_used_google_font,
                "sh_list_view_border": rec.sh_list_view_border,
                "sh_list_row_hover": rec.sh_list_row_hover,
                "sh_even_row_color": rec.sh_even_row_color,
                "sh_odd_row_color": rec.sh_odd_row_color,
                "sh_header_sticky": rec.sh_header_sticky,
                "sh_hover_background_color": rec.sh_hover_background_color,
                "form_element_style": rec.form_element_style,
                "sh_display_product_image_name": rec.sh_display_product_image_name,
                "product_background_color": rec.product_background_color,
            }

            # Check if the file to save had already been modified
            datas = base64.b64encode((content or "\n").encode("utf-8"))

            if attachment:
                # If it was already modified, simply override the corresponding attachment content
                attachment.write({"datas": datas})

            else:
                # If not, create a new attachment
                new_attach = {
                    "name": "POS Theme Settings Variables",
                    "type": "binary",
                    "mimetype": "text/scss",
                    "datas": datas,
                    "url": URL,
                    "public": True,
                    "res_model": "ir.ui.view",
                }

                IrAttachment.sudo().create(new_attach)

                # self.env["ir.qweb"].clear_all_cache()

        return res

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    customer_product_ids = fields.One2many(
        "product.customerinfo", "product_tmpl_id", string="Customer Product References"
    )

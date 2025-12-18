from odoo import fields, models


class ProductCustomerReference(models.Model):
    _name = "product.customerinfo"
    _description = "Product Customer Reference"
    _rec_name = "customer_product_code"

    partner_id = fields.Many2one(
        "res.partner", string="Customer", required=True, ondelete="cascade"
    )
    product_tmpl_id = fields.Many2one(
        "product.template", string="Product", required=True, ondelete="cascade"
    )
    customer_product_code = fields.Char(
        string="Customer Product Code", required=True, index=True
    )
    customer_product_name = fields.Char(string="Customer Product Name")
    _sql_constraints = [
        (
            "uniq_customer_product",
            "unique(partner_id, product_tmpl_id)",
            "A customer can only have one reference per product.",
        ),
        (
            "uniq_customer_code_per_customer",
            "unique(partner_id, customer_product_code)",
            "A customer product code must be unique per customer.",
        ),
    ]

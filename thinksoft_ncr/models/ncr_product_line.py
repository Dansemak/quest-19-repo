from odoo import api, fields, models


class NcrProductLine(models.Model):
    _name = "ncr.product.line"
    _description = "NCR Product Line"

    ncr_claim_id = fields.Many2one("ncr.claim", string="NCR")
    sale_order_id = fields.Many2one("sale.order", string="Sale Order")
    sale_order_line_id = fields.Many2one("sale.order.line", string="Sale Order Line")
    purchase_order_id = fields.Many2one("purchase.order", string="Purchase Order")
    purchase_order_line_id = fields.Many2one(
        "purchase.order.line", string="Purchase Order Line"
    )
    product_id = fields.Many2one("product.product", string="Product")
    product_line_desc = fields.Text(string="Description")
    product_qty = fields.Float(string="Quantity")
    product_cost = fields.Float(string="Cost")
    currency_id = fields.Many2one(
        related="ncr_claim_id.currency_id", store=True, string="Currency", readonly=True
    )
    product_subtotal = fields.Monetary(
        compute="_compute_product_subtotal",
        currency_field="currency_id",
        string="Subtotal",
        store=True,
    )

    @api.depends("product_qty")
    def _compute_product_subtotal(self):
        for line in self:
            line.product_subtotal = line.product_cost * line.product_qty
